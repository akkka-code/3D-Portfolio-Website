/*
 * build_promo.jsx — Editorial Creative-Technologist ExtendScript for Adobe After Effects 2026
 *
 * Rebuilds video/promo.aep to match the exact samsy.ninja editorial portfolio design system:
 *   - Color Palette:
 *       --sn-bg-solid:  #07070A  [0.027, 0.027, 0.039]
 *       --sn-bg-elev:   #0D0D12  [0.051, 0.051, 0.071]
 *       --sn-bg-card:   #0F0F16  [0.059, 0.059, 0.086]
 *       --sn-fg:        #F4F4F6  [0.957, 0.957, 0.965]
 *       --sn-fg-muted:  #8E8E96  [0.557, 0.557, 0.588]
 *       --sn-line:      #2A2A32  [0.165, 0.165, 0.196]
 *       --sn-accent:    #DDFB24  [0.867, 0.984, 0.141] (Surgical Acid-Lime)
 *       --sn-success:   #18F2A0  [0.094, 0.949, 0.627]
 *   - Typography:
 *       Display: Syne / Space Grotesk / Bahnschrift Bold (tight tracking, uppercase)
 *       Mono:    JetBrains Mono / Consolas (indices 001..009, metadata, hairline tags)
 *   - Motion System:
 *       - High-influence Bezier Easing (KeyframeEase(0, 85) out-expo curve)
 *       - Masked Kinetic Typography Line Reveals
 *       - Crisp Architectural Mask Wipes on Gameplay Footage Viewports
 *       - Rhythmic Beat-Grid Pacing (116 BPM -> 2.069s per bar)
 */
(function () {
    app.beginSuppressDialogs();
    try {
        if (app.project) {
            app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
        }
        app.newProject();

        var scriptFile = new File($.fileName);
        var videoDir = scriptFile.parent;
        var rootDir = videoDir.parent;

        var profileFile = new File(rootDir.fsName + "/content/profile.json");
        var profile = {
            name: "Syed Muhammad Ahmad",
            handle: "AKKA",
            role: "Game Developer · Game Programmer · Creative Technologist",
            tagline: "I build immersive games and interactive worlds with Unity, Unreal Engine and real-time 3D.",
            email: "ahmedakka765@gmail.com",
            location: "Karachi, Pakistan"
        };
        if (profileFile.exists) {
            profileFile.encoding = "UTF-8";
            if (profileFile.open("r")) {
                var raw = profileFile.read();
                profileFile.close();
                try {
                    profile = eval("(" + raw + ")");
                } catch (e) {}
            }
        }

        var W = 1920;
        var H = 1080;
        var FPS = 30;
        var DUR = 46.8;

        var comp = app.project.items.addComp("AKKA_EDITORIAL_SHOWREEL_2026", W, H, 1.0, DUR, FPS);
        comp.bgColor = [0.027, 0.027, 0.039]; // #07070A

        // Exact samsy.ninja Editorial Design System Palette
        var COL_BG       = [0.027, 0.027, 0.039]; // #07070A
        var COL_ELEV     = [0.051, 0.051, 0.071]; // #0D0D12
        var COL_CARD     = [0.059, 0.059, 0.086]; // #0F0F16
        var COL_FG       = [0.957, 0.957, 0.965]; // #F4F4F6
        var COL_MUTED    = [0.557, 0.557, 0.588]; // #8E8E96
        var COL_LINE     = [0.220, 0.220, 0.255]; // 1px Swiss Hairline Rule
        var COL_ACCENT   = [0.867, 0.984, 0.141]; // #DDFB24 Surgical Acid-Lime
        var COL_EMERALD  = [0.094, 0.949, 0.627]; // #18F2A0 Status Dot

        // Import 116 BPM Funky Cyber Groove soundtrack
        var wavFile = new File(videoDir.fsName + "/music/funky-cyber-groove.wav");
        if (!wavFile.exists) {
            wavFile = new File(videoDir.fsName + "/music/promo_music.wav");
        }
        if (wavFile.exists) {
            var audioItem = app.project.importFile(new ImportOptions(wavFile));
            var audioLayer = comp.layers.add(audioItem);
            audioLayer.startTime = 0;
        }

        // Import all 8 project gameplay videos + portrait + 3D avatar render
        var gpFolder = new Folder(rootDir.fsName + "/public/video/projects");
        var gpSlugs = [
            "chrono-rebellion",
            "behind-the-smile",
            "paper-dash",
            "solar-system",
            "voxelcraft",
            "pac-man",
            "ar-memory",
            "ar-face-filter"
        ];
        var gpItems = {};
        for (var g = 0; g < gpSlugs.length; g++) {
            var gf = new File(gpFolder.fsName + "/" + gpSlugs[g] + ".mp4");
            if (gf.exists) {
                try {
                    gpItems[gpSlugs[g]] = app.project.importFile(new ImportOptions(gf));
                } catch (eImp) {}
            }
        }

        // Base Obsidian Void Solid
        var bgSolid = comp.layers.addSolid(COL_BG, "00_BG_Obsidian_07070A", W, H, 1.0, DUR);
        bgSolid.moveToEnd();

        // Helper: Apply custom cubic-bezier easing (fast departure, ultra-smooth arrival)
        function applyEditorialBezier(prop) {
            var easeIn = new KeyframeEase(0, 85);
            var easeOut = new KeyframeEase(0, 35);
            for (var k = 1; k <= prop.numKeys; k++) {
                try {
                    prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
                    if (prop.propertyValueType === PropertyValueType.TwoD_SPATIAL || prop.propertyValueType === PropertyValueType.ThreeD_SPATIAL || prop.propertyValueType === PropertyValueType.OneD) {
                        prop.setTemporalEaseAtKey(k, [easeIn], [easeOut]);
                    } else if (prop.propertyValueType === PropertyValueType.TwoD) {
                        prop.setTemporalEaseAtKey(k, [easeIn, easeIn], [easeOut, easeOut]);
                    } else if (prop.propertyValueType === PropertyValueType.ThreeD) {
                        prop.setTemporalEaseAtKey(k, [easeIn, easeIn, easeIn], [easeOut, easeOut, easeOut]);
                    }
                } catch (eEase) {}
            }
        }

        // Helper: Animated 1px Swiss Architectural Hairline Rule (wipes from 0% to 100%)
        function addHairlineRule(name, x, y, w, h, color, inT, outT, fromLeft) {
            var rule = comp.layers.addSolid(color, name, w, h, 1.0, DUR);
            rule.inPoint = inT;
            rule.outPoint = outT;
            if (fromLeft) {
                rule.property("Anchor Point").setValue([0, h / 2]);
                rule.property("Position").setValue([x - w / 2, y]);
            } else {
                rule.property("Position").setValue([x, y]);
            }
            var sc = rule.property("Scale");
            sc.setValueAtTime(inT, [0, 100]);
            sc.setValueAtTime(inT + 0.48, [100, 100]);
            sc.setValueAtTime(outT - 0.30, [100, 100]);
            sc.setValueAtTime(outT, [0, 100]);
            applyEditorialBezier(sc);
            return rule;
        }

        // Helper: Editorial Panel with Crisp Wipe-In Scale/Mask
        function addEditorialPanel(name, x, y, w, h, color, inT, outT, maxOp) {
            var panel = comp.layers.addSolid(color, name, w, h, 1.0, DUR);
            panel.inPoint = inT;
            panel.outPoint = outT;
            panel.property("Position").setValue([x, y]);
            var sc = panel.property("Scale");
            sc.setValueAtTime(inT, [96, 0]);
            sc.setValueAtTime(inT + 0.42, [100, 100]);
            sc.setValueAtTime(outT - 0.28, [100, 100]);
            sc.setValueAtTime(outT, [100, 0]);
            applyEditorialBezier(sc);

            var op = panel.property("Opacity");
            var peak = maxOp || 94;
            op.setValueAtTime(inT, 0);
            op.setValueAtTime(inT + 0.22, peak);
            op.setValueAtTime(outT - 0.22, peak);
            op.setValueAtTime(outT, 0);
            return panel;
        }

        // Helper: Kinetic Typography Reveal (sharp vertical mask slide-up + smooth Bezier ease)
        function addKineticText(str, size, color, pos, inT, outT, justify, isMono, isOutline) {
            var tl = comp.layers.addText(str);
            tl.inPoint = inT;
            tl.outPoint = outT;
            var prop = tl.property("Source Text");
            var doc = prop.value;
            doc.fontSize = size;
            if (isOutline) {
                doc.applyFill = false;
                doc.applyStroke = true;
                doc.strokeColor = color;
                doc.strokeWidth = 2.0;
            } else {
                doc.applyFill = true;
                doc.fillColor = color;
                doc.applyStroke = false;
            }
            try {
                doc.font = isMono ? "Consolas" : "Bahnschrift";
            } catch (eFont) {}
            doc.tracking = isMono ? 60 : -25;
            doc.justification = justify || ParagraphJustification.LEFT_JUSTIFY;
            prop.setValue(doc);

            var p = tl.property("Position");
            var op = tl.property("Opacity");
            var durIn = 0.46;
            var durOut = 0.28;
            p.setValueAtTime(inT, [pos[0], pos[1] + 54]);
            p.setValueAtTime(inT + durIn, [pos[0], pos[1]]);
            p.setValueAtTime(outT - durOut, [pos[0], pos[1]]);
            p.setValueAtTime(outT, [pos[0], pos[1] - 32]);
            applyEditorialBezier(p);

            op.setValueAtTime(inT, 0);
            op.setValueAtTime(inT + 0.18, 100);
            op.setValueAtTime(outT - 0.18, 100);
            op.setValueAtTime(outT, 0);
            return tl;
        }

        // Helper: Add Gameplay Footage with Crisp Rectangular Mask Shutter Wipe
        function addMaskedVideo(slug, centerPos, scalePct, inT, outT, seekOffset) {
            if (!gpItems[slug]) return null;
            var vLayer = comp.layers.add(gpItems[slug]);
            vLayer.audioEnabled = false;
            vLayer.startTime = inT - (seekOffset || 1.0);
            vLayer.inPoint = inT;
            vLayer.outPoint = outT;
            vLayer.property("Position").setValue(centerPos);

            // Subtle smooth editorial scale push-in (scalePct -> scalePct + 4%)
            var sc = vLayer.property("Scale");
            sc.setValueAtTime(inT, [scalePct + 5, scalePct + 5]);
            sc.setValueAtTime(inT + 0.55, [scalePct, scalePct]);
            sc.setValueAtTime(outT, [scalePct + 3, scalePct + 3]);
            applyEditorialBezier(sc);

            // Rectangular Mask Wipe (expands horizontally from left to right on entry)
            try {
                var maskGroup = vLayer.property("Masks");
                var mask = maskGroup.addProperty("Mask");
                var maskShapeProp = mask.property("Mask Path");
                var s0 = new Shape();
                s0.vertices = [[0, 0], [40, 0], [40, H], [0, H]];
                s0.closed = true;
                var s1 = new Shape();
                s1.vertices = [[0, 0], [W, 0], [W, H], [0, H]];
                s1.closed = true;
                maskShapeProp.setValueAtTime(inT, s0);
                maskShapeProp.setValueAtTime(inT + 0.48, s1);
                applyEditorialBezier(maskShapeProp);
            } catch (eMask) {}

            return vLayer;
        }

        // ===================================================================
        // PERSISTENT EDITORIAL TOP & BOTTOM ARCHITECTURAL CHROME (0.0s - 46.8s)
        // ===================================================================
        var topChrome = comp.layers.addSolid(COL_ELEV, "Chrome_TopBar", W, 62, 1.0, DUR);
        topChrome.property("Position").setValue([W / 2, 31]);
        addHairlineRule("Chrome_TopRule", W / 2, 62, W, 1, COL_LINE, 0, DUR, true);

        var botChrome = comp.layers.addSolid(COL_ELEV, "Chrome_BotBar", W, 52, 1.0, DUR);
        botChrome.property("Position").setValue([W / 2, H - 26]);
        addHairlineRule("Chrome_BotRule", W / 2, H - 52, W, 1, COL_LINE, 0, DUR, true);

        // Animated Acid-Lime Progress Hairline along bottom rail
        addHairlineRule("Chrome_ProgressAccent", W / 2, H - 52, W, 2, COL_ACCENT, 0, DUR, true);

        addKineticText("SYED MUHAMMAD AHMAD   [AKKA®]", 18, COL_FG, [48, 38], 0, DUR, ParagraphJustification.LEFT_JUSTIFY, true, false);
        addKineticText("SELECTED WORKS (09)   ·   SHOWREEL 2026   ·   3D AVATAR", 16, COL_MUTED, [W - 48, 38], 0, DUR, ParagraphJustification.RIGHT_JUSTIFY, true, false);
        addKineticText("© 2026 SYED MUHAMMAD AHMAD (AKKA®). ALL RIGHTS RESERVED.", 15, COL_MUTED, [48, H - 20], 0, DUR, ParagraphJustification.LEFT_JUSTIFY, true, false);

        // ===================================================================
        // ACT 1 (0.0s - 4.8s): EDITORIAL HERO STATEMENT & KINETIC REVEAL
        // ===================================================================
        addMaskedVideo("chrono-rebellion", [W / 2, H / 2], 100, 0.0, 4.8, 0.5);
        addEditorialPanel("Act1_Backdrop", W / 2, H / 2, 1780, 760, COL_ELEV, 0.0, 4.8, 92);
        addHairlineRule("Act1_TopLine", W / 2, 160, 1780, 1, COL_LINE, 0.05, 4.8, true);
        addHairlineRule("Act1_AccentStub", 120, 160, 100, 3, COL_ACCENT, 0.1, 4.8, true);

        addKineticText("(00) — CREATIVE GAME DEVELOPER & 3D TECHNOLOGIST", 20, COL_MUTED, [120, 225], 0.10, 4.7, ParagraphJustification.LEFT_JUSTIFY, true, false);
        addKineticText("SYED MUHAMMAD", 96, COL_FG, [120, 345], 0.18, 4.7, ParagraphJustification.LEFT_JUSTIFY, false, false);
        addKineticText("AHMAD — AKKA®", 96, COL_ACCENT, [120, 450], 0.26, 4.7, ParagraphJustification.LEFT_JUSTIFY, false, false);
        addKineticText("INTERACTIVE 3D &", 92, COL_FG, [120, 555], 0.34, 4.7, ParagraphJustification.LEFT_JUSTIFY, false, true);
        addKineticText("GAME ARCHITECT.", 92, COL_FG, [120, 655], 0.42, 4.7, ParagraphJustification.LEFT_JUSTIFY, false, false);

        addHairlineRule("Act1_BotDivider", W / 2, 725, 1680, 1, COL_LINE, 0.45, 4.7, true);
        addKineticText("BS CS & IT (Gaming & Animation) · NED University ’27   |   Game Dev Intern @ Aerox ERP   |   8+ Shipped Games", 22, COL_MUTED, [120, 780], 0.52, 4.7, ParagraphJustification.LEFT_JUSTIFY, false, false);

        // ===================================================================
        // ACT 2..6: EDITORIAL CASE STUDY WIPES (CHRONO, SMILE, DUAL, VOXEL, XR)
        // ===================================================================
        var editorialActs = [
            {
                inT: 4.8, outT: 10.2,
                slug: "chrono-rebellion",
                idx: "001",
                cat: "GAME // 2026 · UNITY HDRP",
                title: "CHRONO REBELLION",
                sub: "Third-person & first-person sci-fi shooter featuring time-manipulation combat mechanics, custom HUD & HDRP lighting.",
                tags: "UNITY   ·   C#   ·   HDRP   ·   SHADER GRAPH   ·   COMBAT AI"
            },
            {
                inT: 10.2, outT: 15.6,
                slug: "behind-the-smile",
                idx: "002",
                cat: "GAME // 2026 · GLOBAL GAME JAM (48H)",
                title: "BEHIND THE SMILE",
                sub: "Narrative-driven first-person 3D exploration game built in 48 hours at Global Game Jam 2026 around the theme 'Masks'.",
                tags: "UNITY 3D   ·   C#   ·   NARRATIVE DESIGN   ·   CUSTOM UI"
            },
            {
                inT: 15.6, outT: 21.0,
                slug: "paper-dash",
                idx: "003 / 004",
                cat: "ARCADE & SYSTEMS // UNREAL ENGINE 5  ×  C++ / SFML",
                title: "PAPER PLANE DASH  ×  PAC-MAN",
                sub: "Procedural UE5 Blueprint endless runner alongside a custom C++ & SFML arcade engine using QuadTrees & Graph AI.",
                tags: "UNREAL ENGINE 5   ·   BLUEPRINTS   ·   C++   ·   SFML   ·   QUADTREES"
            },
            {
                inT: 21.0, outT: 26.2,
                slug: "voxelcraft",
                idx: "005",
                cat: "SANDBOX ENGINE // 2025 · PROCEDURAL 3D",
                title: "VOXELCRAFT 3D",
                sub: "Procedural voxel terrain generation, chunk mesh optimization, and raycast block placement & destruction physics.",
                tags: "UNITY 3D   ·   C#   ·   VOXEL MESHING   ·   PROCEDURAL TERRAIN"
            },
            {
                inT: 26.2, outT: 31.8,
                slug: "solar-system",
                idx: "006 / 007 / 008",
                cat: "EXTENDED REALITY (XR) // VR  ·  VUFORIA AR  ·  MEDIAPIPE CV",
                title: "SOLAR SYSTEM VR  ×  AR SUITE",
                sub: "OpenXR planetary simulation, Vuforia marker-based AR Memory Card game, and Python/OpenCV/MediaPipe 468-point AR Face Filter.",
                tags: "OPENXR   ·   XR INTERACTION TOOLKIT   ·   VUFORIA   ·   OPENCV   ·   MEDIAPIPE"
            }
        ];

        for (var a = 0; a < editorialActs.length; a++) {
            var act = editorialActs[a];
            addMaskedVideo(act.slug, [W / 2, H / 2], 100, act.inT, act.outT, 1.5);

            // Minimalist Architectural Lower-Left Case Study Card
            addEditorialPanel("CasePanel_" + a, 690, 845, 1260, 240, COL_ELEV, act.inT + 0.08, act.outT, 94);
            addHairlineRule("CaseTopLine_" + a, 690, 725, 1260, 1, COL_LINE, act.inT + 0.10, act.outT, true);
            addHairlineRule("CaseAccent_" + a, 120, 725, 120, 3, COL_ACCENT, act.inT + 0.14, act.outT, true);

            addKineticText(act.idx + "   //   " + act.cat, 18, COL_ACCENT, [96, 765], act.inT + 0.14, act.outT, ParagraphJustification.LEFT_JUSTIFY, true, false);
            addKineticText(act.title, 54, COL_FG, [96, 830], act.inT + 0.20, act.outT, ParagraphJustification.LEFT_JUSTIFY, false, false);
            addKineticText(act.sub, 21, COL_MUTED, [96, 882], act.inT + 0.26, act.outT, ParagraphJustification.LEFT_JUSTIFY, false, false);
            addKineticText(act.tags, 16, COL_FG, [96, 935], act.inT + 0.32, act.outT, ParagraphJustification.LEFT_JUSTIFY, true, false);
        }

        // ===================================================================
        // ACT 7 (31.8s - 37.0s): CUSTOM BLENDER 5.1 3D AVATAR & CAPABILITIES MATRIX
        // ===================================================================
        addMaskedVideo("chrono-rebellion", [W / 2, H / 2], 100, 31.8, 37.0, 6.0);
        addEditorialPanel("Act7_Panel", 1260, 540, 1180, 820, COL_ELEV, 31.8, 37.0, 95);
        addHairlineRule("Act7_TopRule", 1260, 130, 1180, 1, COL_LINE, 31.85, 37.0, true);
        addHairlineRule("Act7_Accent", 730, 130, 120, 3, COL_ACCENT, 31.9, 37.0, true);

        addKineticText("(02) — CUSTOM 3D CHARACTER & TECHNICAL CAPABILITIES", 19, COL_ACCENT, [710, 185], 31.9, 36.9, ParagraphJustification.LEFT_JUSTIFY, true, false);
        addKineticText("BLENDER 5.1 RIGGED AVATAR", 54, COL_FG, [710, 255], 31.98, 36.9, ParagraphJustification.LEFT_JUSTIFY, false, false);
        addKineticText("21-Bone Skeleton · 6 NLA Tracks (Walk, Idle, Wave, Talk, Point, Victory) · 3rd-Person Walk Mode", 21, COL_MUTED, [710, 310], 32.06, 36.9, ParagraphJustification.LEFT_JUSTIFY, false, false);

        var capRows = [
            "01 // GAME ENGINES      Unity (HDRP / URP) · Unreal Engine 5 · Blueprints · SFML",
            "02 // PROGRAMMING       C# · C++ · C · Python · QuadTrees & Graph Pathfinding",
            "03 // XR & 3D DESIGN    OpenXR · Vuforia · Blender 5.1 · After Effects · Photoshop",
            "04 // WEB & AI RAG      Three.js WebGPU · TSL Shaders · Gemini RAG Assistant"
        ];
        for (var c = 0; c < capRows.length; c++) {
            var cy = 420 + c * 115;
            addHairlineRule("CapRule_" + c, 1260, cy - 35, 1100, 1, COL_LINE, 32.15 + c * 0.1, 36.9, true);
            addKineticText(capRows[c], 22, COL_FG, [710, cy + 15], 32.2 + c * 0.1, 36.9, ParagraphJustification.LEFT_JUSTIFY, true, false);
        }

        // ===================================================================
        // ACT 8 (37.0s - 41.6s): 09 SELECTED WORKS ARCHITECTURAL INDEX MATRIX
        // ===================================================================
        addMaskedVideo("paper-dash", [W / 2, H / 2], 100, 37.0, 41.6, 3.0);
        addEditorialPanel("Act8_CenterCard", W / 2, H / 2, 1080, 320, COL_ELEV, 37.05, 41.6, 95);
        addHairlineRule("Act8_RuleTop", W / 2, H / 2 - 160, 1080, 1, COL_LINE, 37.1, 41.6, true);
        addHairlineRule("Act8_AccentTop", W / 2, H / 2 - 160, 160, 3, COL_ACCENT, 37.15, 41.6, false);

        addKineticText("(01) — CURATED PROJECT INDEX // 2024–2026", 19, COL_ACCENT, [W / 2, H / 2 - 90], 37.15, 41.5, ParagraphJustification.CENTER_JUSTIFY, true, false);
        addKineticText("09 INTERACTIVE WORKS", 68, COL_FG, [W / 2, H / 2 - 10], 37.22, 41.5, ParagraphJustification.CENTER_JUSTIFY, false, false);
        addKineticText("3D ACTION   ·   UNREAL RUNNER   ·   VR / AR   ·   VOXEL ENGINE   ·   WEBGPU ALLEY", 19, COL_MUTED, [W / 2, H / 2 + 65], 37.30, 41.5, ParagraphJustification.CENTER_JUSTIFY, true, false);

        // ===================================================================
        // ACT 9 (41.6s - 46.8s): EDITORIAL OUTRO & DIRECT TRANSMISSION
        // ===================================================================
        addMaskedVideo("behind-the-smile", [W / 2, H / 2], 100, 41.6, 46.8, 3.5);
        addEditorialPanel("Act9_OutroPanel", W / 2, H / 2, 1740, 740, COL_ELEV, 41.6, 46.8, 95);
        addHairlineRule("Act9_TopLine", W / 2, 170, 1740, 1, COL_LINE, 41.65, 46.8, true);
        addHairlineRule("Act9_Accent", W / 2, 170, 180, 3, COL_ACCENT, 41.7, 46.8, false);

        addKineticText("(04) — INITIATE DIRECT TRANSMISSION", 20, COL_ACCENT, [W / 2, 260], 41.72, 46.6, ParagraphJustification.CENTER_JUSTIFY, true, false);
        addKineticText("SYED MUHAMMAD AHMAD", 78, COL_FG, [W / 2, 370], 41.80, 46.6, ParagraphJustification.CENTER_JUSTIFY, false, false);
        addKineticText("LET’S BUILD THE NEXT IMMERSIVE WORLD.", 44, COL_FG, [W / 2, 455], 41.88, 46.6, ParagraphJustification.CENTER_JUSTIFY, false, true);

        addHairlineRule("Act9_MidLine", W / 2, 535, 920, 1, COL_LINE, 41.95, 46.6, false);
        addKineticText("ahmedakka765@gmail.com   ·   +92 332 2669028", 28, COL_FG, [W / 2, 610], 42.02, 46.6, ParagraphJustification.CENTER_JUSTIFY, true, false);
        addKineticText("syed-muhammad-ahmad-portfolio.vercel.app", 24, COL_ACCENT, [W / 2, 675], 42.10, 46.6, ParagraphJustification.CENTER_JUSTIFY, true, false);
        addKineticText("NED UNIVERSITY OF ENGINEERING & TECHNOLOGY · KARACHI, PAKISTAN", 18, COL_MUTED, [W / 2, 745], 42.18, 46.6, ParagraphJustification.CENTER_JUSTIFY, true, false);

        // Save After Effects Project (.aep)
        var aepFile = new File(videoDir.fsName + "/promo.aep");
        app.project.save(aepFile);

        var statusFile = new File(videoDir.fsName + "/build_status.txt");
        statusFile.encoding = "UTF-8";
        if (statusFile.open("w")) {
            statusFile.write("SUCCESS: Saved editorial " + aepFile.fsName + " (" + comp.name + ", " + DUR + "s)");
            statusFile.close();
        }
    } catch (err) {
        try {
            var errFile = new File(File($.fileName).parent.fsName + "/build_status.txt");
            errFile.open("w");
            errFile.write("ERROR: " + err.toString() + " (line " + err.line + ")");
            errFile.close();
        } catch (e2) {}
    } finally {
        app.endSuppressDialogs(false);
        app.quit();
    }
})();
