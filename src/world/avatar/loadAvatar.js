import * as THREE from "three/webgpu";
import { getGltfLoader } from "../loaders/createGltfLoaders.js";

const AVATAR_PATH = "/models/avatar.glb";

/**
 * Alley placement near the camera start so the visitor immediately sees the
 * developer's 3D avatar standing in the open cyberpunk alley.
 * Ground plane is at y = -5.50.
 */
export const AVATAR_START = {
  position: [-133.2, -5.48, 32.1],
  rotationY: Math.PI * 0.44, // Facing down the alley (+X)
  scale: 1.0,
};

/**
 * Camera position right behind the avatar for Third-Person Walk mode
 * (clear of the Quadra car collider so pressing W walks straight down the alley).
 */
export const THIRD_PERSON_CAMERA_START = {
  position: [-135.35, -3.95, 32.45],
  target: [-115.0, -3.65, 30.5],
};

function lerpAngle(current, target, t) {
  let diff = ((target - current + Math.PI) % (Math.PI * 2)) - Math.PI;
  if (diff < -Math.PI) diff += Math.PI * 2;
  return current + diff * Math.min(1, t);
}

function convertToNodeMaterials(root) {
  root.traverse((child) => {
    if (!child.isMesh) return;
    child.castShadow = true;
    child.receiveShadow = true;

    const convertOne = (mat) => {
      if (!mat || mat.isMeshStandardNodeMaterial) return mat;
      const nodeMat = new THREE.MeshStandardNodeMaterial();
      nodeMat.name = mat.name || "AvatarMat";
      nodeMat.color.copy(mat.color ?? new THREE.Color(0xffffff));
      nodeMat.roughness = mat.roughness ?? 0.5;
      nodeMat.metalness = mat.metalness ?? 0.0;
      if (mat.emissive) {
        nodeMat.emissive.copy(mat.emissive);
        nodeMat.emissiveIntensity = mat.emissiveIntensity ?? 1.0;
      }
      return nodeMat;
    };

    if (Array.isArray(child.material)) {
      child.material = child.material.map(convertOne);
    } else if (child.material) {
      child.material = convertOne(child.material);
    }
  });
}

export async function loadAvatar(renderer, scene) {
  const loader = getGltfLoader(renderer);
  let gltf;
  try {
    gltf = await loader.loadAsync(AVATAR_PATH);
  } catch (error) {
    console.warn("[avatar] Could not load /models/avatar.glb:", error);
    return null;
  }

  const root = new THREE.Group();
  root.name = "PortfolioAvatarRoot";
  root.position.set(...AVATAR_START.position);
  root.rotation.y = AVATAR_START.rotationY;
  root.scale.setScalar(AVATAR_START.scale);

  const model = gltf.scene;
  convertToNodeMaterials(model);
  root.add(model);

  // Subtle holographic cyan base ring under the avatar's feet
  const ringGeo = new THREE.RingGeometry(0.42, 0.52, 48);
  ringGeo.rotateX(-Math.PI / 2);
  const ringMat = new THREE.MeshStandardNodeMaterial({
    color: new THREE.Color(0x00e5ff),
    emissive: new THREE.Color(0x00e5ff),
    emissiveIntensity: 2.8,
    roughness: 0.2,
    side: THREE.DoubleSide,
  });
  const baseRing = new THREE.Mesh(ringGeo, ringMat);
  baseRing.position.y = 0.015;
  baseRing.name = "AvatarHoloRing";
  root.add(baseRing);

  // Dedicated key + rim point lights so the avatar pops in the dark alley
  const keyLight = new THREE.PointLight(0x00e5ff, 2.4, 5.0, 1.5);
  keyLight.position.set(0.9, 1.75, 1.1);
  root.add(keyLight);

  const rimLight = new THREE.PointLight(0xff2bd6, 2.0, 4.5, 1.5);
  rimLight.position.set(-0.9, 1.65, -0.8);
  root.add(rimLight);

  if (scene) {
    scene.add(root);
  }

  // Locate bones and morph-target mesh (HeadMesh)
  let headBone = null;
  let headMorphMesh = null;
  const bones = {};
  model.traverse((obj) => {
    if (obj.isBone) {
      bones[obj.name] = obj;
      if (obj.name === "Head") {
        headBone = obj;
      }
    }
    if (obj.isMesh && obj.morphTargetDictionary && obj.morphTargetInfluences) {
      headMorphMesh = obj;
    }
  });

  // Set up AnimationMixer & clips (Idle, Walk, Wave, Talk, Point, Victory)
  const mixer = new THREE.AnimationMixer(model);
  const actions = {};
  for (const clip of gltf.animations || []) {
    const action = mixer.clipAction(clip);
    actions[clip.name] = action;
  }

  let currentActionName = "Idle";
  if (actions.Idle) {
    actions.Idle.play();
  }

  function playAnimation(name, { loopOnce = false, fade = 0.22 } = {}) {
    const next = actions[name];
    if (!next) return;
    if (currentActionName === name && next.isRunning()) return;
    const prev = actions[currentActionName];
    if (prev && prev !== next) {
      prev.fadeOut(fade);
    }
    next.reset();
    if (loopOnce) {
      next.setLoop(THREE.LoopOnce, 1);
      next.clampWhenFinished = true;
    } else {
      next.setLoop(THREE.LoopRepeat, Infinity);
      next.clampWhenFinished = false;
    }
    next.fadeIn(fade).play();
    currentActionName = name;
  }

  mixer.addEventListener("finished", () => {
    if (currentActionName !== "Idle" && currentActionName !== "Walk" && actions.Idle) {
      playAnimation("Idle");
    }
  });

  // Expression & third-person state
  const exprState = {
    speaking: false,
    smiling: false,
    blinkTimer: 0,
    nextBlinkAt: 2.6,
    talkPhase: 0,
    walkCyclePhase: 0,
    pointerNdc: new THREE.Vector2(0, 0),
    hasPointer: false,
    turntableSpeed: 0,
    thirdPerson: true, // Default ON so walking walks with the avatar
  };

  const forwardVec = new THREE.Vector3();
  const targetAvatarPos = new THREE.Vector3(...AVATAR_START.position);
  const prevAvatarPos = new THREE.Vector3(...AVATAR_START.position);
  const listeners = new Set();

  function notifyPerspectiveChange() {
    for (const fn of listeners) {
      try {
        fn(exprState.thirdPerson);
      } catch {
        /* ignore */
      }
    }
  }

  window.addEventListener(
    "pointermove",
    (e) => {
      exprState.pointerNdc.x = (e.clientX / window.innerWidth) * 2 - 1;
      exprState.pointerNdc.y = -((e.clientY / window.innerHeight) * 2 - 1);
      exprState.hasPointer = true;
    },
    { passive: true },
  );

  // Allow pressing 'V' key (when not typing in an input) to toggle 3rd-person / 1st-person
  window.addEventListener("keydown", (e) => {
    if (e.code !== "KeyV" || e.repeat) return;
    const tag = e.target?.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || e.target?.isContentEditable) {
      return;
    }
    exprState.thirdPerson = !exprState.thirdPerson;
    notifyPerspectiveChange();
  });

  function setMorph(name, value) {
    if (!headMorphMesh) return;
    const idx = headMorphMesh.morphTargetDictionary?.[name];
    if (idx !== undefined) {
      headMorphMesh.morphTargetInfluences[idx] = THREE.MathUtils.clamp(value, 0, 1);
    }
  }

  function triggerGesture(name = "Wave") {
    if (!actions[name]) return;
    const isLoop = name === "Idle" || name === "Talk" || name === "Walk";
    playAnimation(name, { loopOnce: !isLoop });
    if (name === "Wave" || name === "Victory") {
      exprState.smiling = true;
      setTimeout(() => {
        exprState.smiling = false;
      }, 2400);
    }
  }

  function setSpeaking(speaking) {
    exprState.speaking = Boolean(speaking);
    if (exprState.speaking) {
      playAnimation("Talk");
    } else if (currentActionName === "Talk") {
      playAnimation("Idle");
      setMorph("MouthOpen", 0);
    }
  }

  function rotateBy(deltaYaw) {
    root.rotation.y += deltaYaw;
  }

  function update(delta, camera, walkControls = null, introActive = false) {
    mixer.update(delta);

    // Subtle holo-ring pulse
    baseRing.rotation.z += delta * 0.65;
    if (exprState.turntableSpeed !== 0) {
      root.rotation.y += delta * exprState.turntableSpeed;
    }

    // -------------------------------------------------------------------------
    // THIRD-PERSON AVATAR WALK CONTROLLER
    // When walk mode is active (after intro) and thirdPerson is enabled, the
    // avatar walks ahead of the camera and plays the Walk animation when moving.
    // -------------------------------------------------------------------------
    const isWalkMode = Boolean(walkControls?.isActive?.()) && !introActive;

    if (isWalkMode && exprState.thirdPerson && camera) {
      camera.getWorldDirection(forwardVec);
      forwardVec.y = 0;
      if (forwardVec.lengthSq() > 1e-5) {
        forwardVec.normalize();
      } else {
        forwardVec.set(1, 0, 0);
      }

      // Position avatar 2.15m ahead of the camera on the ground plane
      const followDist = 2.15;
      const groundY = camera.position.y - 1.55 + 0.02;
      targetAvatarPos.set(
        camera.position.x + forwardVec.x * followDist,
        groundY,
        camera.position.z + forwardVec.z * followDist,
      );

      prevAvatarPos.copy(root.position);
      const posLerp = Math.min(1, delta * 14);
      root.position.lerp(targetAvatarPos, posLerp);

      const moveDx = root.position.x - prevAvatarPos.x;
      const moveDz = root.position.z - prevAvatarPos.z;
      const moveStep = Math.hypot(moveDx, moveDz);
      const isMoving = Boolean(walkControls.isMoving?.()) || moveStep > 0.004;
      const horizSpeed = walkControls.getHorizontalSpeed?.() ?? (moveStep / Math.max(delta, 0.001));

      if (isMoving) {
        // Face movement direction (or camera forward if rotating in place)
        const moveYaw =
          moveStep > 0.0025
            ? Math.atan2(moveDx, moveDz)
            : Math.atan2(forwardVec.x, forwardVec.z);
        root.rotation.y = lerpAngle(root.rotation.y, moveYaw, delta * 12);

        const speedRatio = THREE.MathUtils.clamp(horizSpeed / 3.0, 0.75, 1.85);
        if (actions.Walk) {
          actions.Walk.timeScale = speedRatio;
          if (currentActionName !== "Walk") {
            playAnimation("Walk", { loopOnce: false, fade: 0.16 });
          }
        }

        // Procedural stride reinforcement so leg & arm swing stays super visible in 3rd-person
        exprState.walkCyclePhase += delta * 8.5 * speedRatio;
        const swing = Math.sin(exprState.walkCyclePhase);
        if (bones["UpperLeg.L"] && bones["UpperLeg.R"]) {
          bones["UpperLeg.L"].rotation.x = swing * 0.52;
          bones["UpperLeg.R"].rotation.x = -swing * 0.52;
        }
        if (bones["LowerLeg.L"] && bones["LowerLeg.R"]) {
          bones["LowerLeg.L"].rotation.x = Math.max(0, -swing) * -0.48;
          bones["LowerLeg.R"].rotation.x = Math.max(0, swing) * -0.48;
        }
        if (bones["UpperArm.L"] && bones["UpperArm.R"]) {
          bones["UpperArm.L"].rotation.x = -swing * 0.38;
          bones["UpperArm.R"].rotation.x = swing * 0.38;
        }
      } else {
        // Idle in 3rd-person: face down the camera's look direction
        const lookYaw = Math.atan2(forwardVec.x, forwardVec.z);
        root.rotation.y = lerpAngle(root.rotation.y, lookYaw, delta * 6);
        if (currentActionName === "Walk") {
          playAnimation("Idle", { loopOnce: false, fade: 0.22 });
        }
      }
    } else if (!isWalkMode && introActive) {
      // During intro, face toward the camera so the avatar greets the viewer
      root.position.set(...AVATAR_START.position);
      root.rotation.y = -0.45;
    }

    // Automatic periodic eye blink
    exprState.blinkTimer += delta;
    if (exprState.blinkTimer >= exprState.nextBlinkAt) {
      const t = (exprState.blinkTimer - exprState.nextBlinkAt) / 0.18;
      if (t <= 1.0) {
        setMorph("Blink", Math.sin(t * Math.PI));
      } else {
        setMorph("Blink", 0);
        exprState.blinkTimer = 0;
        exprState.nextBlinkAt = 2.4 + Math.random() * 2.8;
      }
    }

    // Smile morph smoothing
    if (headMorphMesh) {
      const idx = headMorphMesh.morphTargetDictionary?.Smile;
      if (idx !== undefined) {
        const cur = headMorphMesh.morphTargetInfluences[idx] || 0;
        const target = exprState.smiling ? 0.85 : 0.15;
        headMorphMesh.morphTargetInfluences[idx] = THREE.MathUtils.lerp(cur, target, delta * 6);
      }
    }

    // Lip-sync MouthOpen animation while AI voice / chatbot speaks
    if (exprState.speaking) {
      exprState.talkPhase += delta * 15;
      const mouth = 0.25 + 0.65 * Math.abs(Math.sin(exprState.talkPhase) * Math.cos(exprState.talkPhase * 0.65));
      setMorph("MouthOpen", mouth);
    }

    // Subtle mouse-tracking head orientation when not walking away in 3rd-person
    if (headBone && exprState.hasPointer && (!isWalkMode || !exprState.thirdPerson)) {
      const targetYaw = THREE.MathUtils.clamp(exprState.pointerNdc.x * 0.35, -0.38, 0.38);
      const targetPitch = THREE.MathUtils.clamp(-exprState.pointerNdc.y * 0.22, -0.25, 0.25);
      headBone.rotation.z = THREE.MathUtils.lerp(headBone.rotation.z, targetYaw, 0.18);
      headBone.rotation.x = THREE.MathUtils.lerp(headBone.rotation.x, targetPitch, 0.18);
    }
  }

  return {
    root,
    model,
    mixer,
    actions: Object.keys(actions),
    playAnimation,
    triggerGesture,
    setSpeaking,
    rotateBy,
    setTurntable: (speed) => {
      exprState.turntableSpeed = speed;
    },
    isThirdPerson: () => exprState.thirdPerson,
    setThirdPerson: (enabled) => {
      exprState.thirdPerson = Boolean(enabled);
      notifyPerspectiveChange();
    },
    toggleThirdPerson: () => {
      exprState.thirdPerson = !exprState.thirdPerson;
      notifyPerspectiveChange();
      return exprState.thirdPerson;
    },
    onPerspectiveChange: (fn) => {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    getCurrentAnimation: () => currentActionName,
    update,
  };
}
