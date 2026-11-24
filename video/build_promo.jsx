/*
 * build_promo.jsx — Editorial Creative-Technologist ExtendScript for Adobe After Effects 2027
 *
 * Rebuilds video/promo.aep to match the exact 9-act, 46.8s @ 30fps portfolio showreel
 * (public/video/promo.mp4) and samsy.ninja editorial design system:
 *   - Color Palette:
 *       --sn-bg-solid:  #07070A  [0.027, 0.027, 0.039]
 *       --sn-bg-elev:   #0D0D12  [0.051, 0.051, 0.071]
 *       --sn-bg-card:   #0F0F16  [0.059, 0.059, 0.086]
 *       --sn-fg:        #F4F4F6  [0.957, 0.957, 0.965]
 *       --sn-fg-muted:  #8E8E96  [0.557, 0.557, 0.588]
 *       --sn-line:      #2A2A32  [0.165, 0.165, 0.196]
 *       --sn-accent:    #DDFB24  [0.867, 0.984, 0.141] (Surgical Acid-Lime)
 *       --sn-success:   #18F2A0  [0.094, 0.949, 0.627]
 *   - Project Structure:
 *       01_Compositions / 02_Gameplay_Footage / 03_HUD_Overlays / 04_Stills_&_Avatar / 05_Audio / 06_Solids
 *   - Active Layers:
 *       Exact multi-viewport gameplay layouts (Quad-Grid, Fullscreen, Dual Split, Triple XR)
 *       + cubic-bezier animated editorial HUD overlay PNGs (hud_scene1_intro..hud_scene9_outro)
 *       + 116 BPM soundtrack with fade-in/fade-out
 *   - Editable Native Layers (eye toggled OFF by default to prevent double-rendering):
 *       [Editable Native Text] & [Editable Native Panel] layers for direct AE text edits.
 */
(function () {
    app.beginSuppressDialogs();
    try {
        app.preferences.savePrefAsLong("Main Pref Section v2", "Pref_SCRIPTING_FILE_NETWORK_SECURITY", 1);
        app.preferences.saveToDisk();
    } catch (ePref) {}
    var scriptFile = new File($.fileName);
    var videoDir = scriptFile.parent;
    var rootDir = videoDir.parent;

    function writeStatus(msg) {
        try {
            var sf = new File(videoDir.fsName + "/build_status.txt");
            sf.encoding = "UTF-8";
            if (sf.open("w")) {
                sf.write(msg);
                sf.close();
            }
        } catch (eLog) {}
    }

    try {
        if (app.project) {
            app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
        }
        app.newProject();

        var W = 1920;
        var H = 1080;
        var FPS = 30;
        var DUR = 46.8;

        // Exact samsy.ninja Editorial Design System Palette
        var COL_BG       = [0.027, 0.027, 0.039]; // #07070A
        var COL_ELEV     = [0.051, 0.051, 0.071]; // #0D0D12
        var COL_FG       = [0.957, 0.957, 0.965]; // #F4F4F6
        var COL_MUTED    = [0.557, 0.557, 0.588]; // #8E8E96
        var COL_LINE     = [0.220, 0.220, 0.255]; // 1px Swiss Hairline Rule
        var COL_ACCENT   = [0.867, 0.984, 0.141]; // #DDFB24 Surgical Acid-Lime

        // ===================================================================
        // ORGANIZED PROJECT PANEL FOLDERS
        // ===================================================================
        var folderComps   = app.project.items.addFolder("01_Compositions");
        var folderFootage = app.project.items.addFolder("02_Gameplay_Footage");
        var folderHuds    = app.project.items.addFolder("03_HUD_Overlays");
        var folderStills  = app.project.items.addFolder("04_Stills_&_Avatar");
        var folderAudio   = app.project.items.addFolder("05_Audio");
        var folderSolids  = app.project.items.addFolder("06_Solids");

        var comp = folderComps.items.addComp("AKKA_EDITORIAL_SHOWREEL_2026", W, H, 1.0, DUR, FPS);
        comp.bgColor = COL_BG;

        // Import 116 BPM Funky Cyber Groove soundtrack
        var wavFile = new File(videoDir.fsName + "/music/funky-cyber-groove.wav");
        if (!wavFile.exists) {
            wavFile = new File(videoDir.fsName + "/music/promo_music.wav");
        }
        var audioItem = null;
        if (wavFile.exists) {
            try {
                audioItem = app.project.importFile(new ImportOptions(wavFile));
                audioItem.parentFolder = folderAudio;
            } catch (eAud) {}
        }

        // Import all 8 project gameplay videos
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
                    var gItem = app.project.importFile(new ImportOptions(gf));
                    gItem.parentFolder = folderFootage;
                    gpItems[gpSlugs[g]] = gItem;
                } catch (eImp) {}
            }
        }

        // Import all 9 editorial HUD overlay PNGs
        var ovrFolder = new Folder(videoDir.fsName + "/overlays");
        var ovrNames = [
            "hud_scene1_intro.png",
            "hud_scene2_chrono.png",
            "hud_scene3_smile.png",
            "hud_scene4_dual.png",
            "hud_scene5_voxel.png",
            "hud_scene6_xr.png",
            "hud_scene7_avatar.png",
            "hud_scene8_quad.png",
            "hud_scene9_outro.png"
        ];
        var hudItems = {};
        for (var h = 0; h < ovrNames.length; h++) {
            var hf = new File(ovrFolder.fsName + "/" + ovrNames[h]);
            if (hf.exists) {
                try {
                    var hItem = app.project.importFile(new ImportOptions(hf));
                    hItem.parentFolder = folderHuds;
                    hudItems[ovrNames[h]] = hItem;
                } catch (eHud) {}
            }
        }

        // Import portrait & 3D avatar render stills
        var portraitFile = new File(rootDir.fsName + "/public/images/ahmad-1.jpg");
        var portraitItem = null;
        if (portraitFile.exists) {
            try {
                portraitItem = app.project.importFile(new ImportOptions(portraitFile));
                portraitItem.parentFolder = folderStills;
            } catch (ePort) {}
        }

        var avatarFile = new File(rootDir.fsName + "/blender/avatar_preview.png");
        var avatarItem = null;
        if (avatarFile.exists) {
            try {
                avatarItem = app.project.importFile(new ImportOptions(avatarFile));
                avatarItem.parentFolder = folderStills;
            } catch (eAv) {}
        }

        // ===================================================================
        // COMPOSITION MARKERS FOR ALL 9 ACTS
        // ===================================================================
        var actMarkers = [
            [0.0,  "Act 1 // (00) Hero Statement"],
            [4.8,  "Act 2 // 001 Chrono Rebellion"],
            [10.2, "Act 3 // 002 Behind the Smile"],
            [15.6, "Act 4 // 003 x 006 Dual Engine Comparison"],
            [21.0, "Act 5 // 005 Voxelcraft 3D"],
            [26.2, "Act 6 // 004 x 007 x 008 Extended Reality Suite"],
            [31.8, "Act 7 // (02) 3D Avatar & Capabilities"],
            [37.0, "Act 8 // (01) 09 Selected Works Matrix"],
            [41.6, "Act 9 // (04) Direct Transmission Outro"]
        ];
        try {
            var mp = comp.markerProperty;
            for (var m = 0; m < actMarkers.length; m++) {
                mp.setValueAtTime(actMarkers[m][0], new MarkerValue(actMarkers[m][1]));
            }
        } catch (eMk) {}

        // ===================================================================
        // EASING & LAYER HELPERS
        // ===================================================================
        function applyEditorialBezier(prop) {
            var easeIn = new KeyframeEase(0, 85);
            var easeOut = new KeyframeEase(0, 35);
            for (var k = 1; k <= prop.numKeys; k++) {
                try {
                    prop.setInterpolationTypeAtKey(k, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
                    if (
                        prop.propertyValueType === PropertyValueType.TwoD_SPATIAL ||
                        prop.propertyValueType === PropertyValueType.ThreeD_SPATIAL ||
                        prop.propertyValueType === PropertyValueType.OneD
                    ) {
                        prop.setTemporalEaseAtKey(k, [easeIn], [easeOut]);
                    } else if (prop.propertyValueType === PropertyValueType.TwoD) {
                        prop.setTemporalEaseAtKey(k, [easeIn, easeIn], [easeOut, easeOut]);
                    } else if (prop.propertyValueType === PropertyValueType.ThreeD) {
                        prop.setTemporalEaseAtKey(k, [easeIn, easeIn, easeIn], [easeOut, easeOut, easeOut]);
                    }
                } catch (eEase) {}
            }
        }

        function computeCoverScale(item, targetW, targetH) {
            var iw = item.width > 0 ? item.width : 1920;
            var ih = item.height > 0 ? item.height : 1080;
            return Math.max((targetW / iw) * 100, (targetH / ih) * 100);
        }

        function applyCompRectMask(layer, item, boxX, boxY, boxW, boxH, centerX, centerY, scalePct) {
            try {
                var iw = item.width > 0 ? item.width : 1920;
                var ih = item.height > 0 ? item.height : 1080;
                var s = scalePct / 100.0;
                var x0 = ((boxX - centerX) / s) + (iw / 2);
                var y0 = ((boxY - centerY) / s) + (ih / 2);
                var x1 = (((boxX + boxW) - centerX) / s) + (iw / 2);
                var y1 = (((boxY + boxH) - centerY) / s) + (ih / 2);

                var maskGroup = layer.property("Masks");
                var mask = maskGroup.addProperty("Mask");
                var maskShapeProp = mask.property("Mask Path");
                var shp = new Shape();
                shp.vertices = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
                shp.closed = true;
                maskShapeProp.setValue(shp);
            } catch (eMask) {}
        }

        // Viewport-cropped gameplay clip (Quad-Grid, Dual Split, Triple XR)
        function addViewportVideo(layerName, slug, boxX, boxY, boxW, boxH, inT, outT, seekSec, opacityPct) {
            var item = gpItems[slug];
            if (!item) return null;
            var vLayer = comp.layers.add(item);
            vLayer.name = layerName;
            vLayer.audioEnabled = false;
            vLayer.startTime = inT - (seekSec || 0.5);
            vLayer.inPoint = inT;
            vLayer.outPoint = outT;

            var cx = boxX + boxW / 2;
            var cy = boxY + boxH / 2;
            var coverScale = computeCoverScale(item, boxW, boxH);

            vLayer.property("Position").setValue([cx, cy]);
            vLayer.property("Scale").setValue([coverScale, coverScale]);
            if (typeof opacityPct === "number" && opacityPct < 100) {
                vLayer.property("Opacity").setValue(opacityPct);
            }
            applyCompRectMask(vLayer, item, boxX, boxY, boxW, boxH, cx, cy, coverScale);
            return vLayer;
        }

        // Fullscreen 1920x1080 gameplay clip with smooth horizontal pan & gentle push-in
        function addFullScreenVideo(layerName, slug, inT, outT, seekSec) {
            var item = gpItems[slug];
            if (!item) return null;
            var vLayer = comp.layers.add(item);
            vLayer.name = layerName;
            vLayer.audioEnabled = false;
            vLayer.startTime = inT - (seekSec || 1.0);
            vLayer.inPoint = inT;
            vLayer.outPoint = outT;

            var baseCover = computeCoverScale(item, W, H) * 1.05;
            var p = vLayer.property("Position");
            p.setValueAtTime(inT, [W / 2 - 28, H / 2]);
            p.setValueAtTime((inT + outT) / 2, [W / 2 + 28, H / 2]);
            p.setValueAtTime(outT, [W / 2 - 12, H / 2]);
            applyEditorialBezier(p);

            var sc = vLayer.property("Scale");
            sc.setValueAtTime(inT, [baseCover + 3, baseCover + 3]);
            sc.setValueAtTime(inT + 0.55, [baseCover, baseCover]);
            sc.setValueAtTime(outT, [baseCover + 2.5, baseCover + 2.5]);
            applyEditorialBezier(sc);

            return vLayer;
        }

        // Still image layer (portrait or 3D avatar) placed inside its frame
        function addStillLayer(layerName, item, boxX, boxY, boxW, boxH, inT, outT, enabled) {
            if (!item) return null;
            var sLayer = comp.layers.add(item);
            sLayer.name = layerName;
            sLayer.inPoint = inT;
            sLayer.outPoint = outT;
            var cx = boxX + boxW / 2;
            var cy = boxY + boxH / 2;
            var coverScale = computeCoverScale(item, boxW, boxH);
            sLayer.property("Position").setValue([cx, cy]);
            sLayer.property("Scale").setValue([coverScale, coverScale]);
            applyCompRectMask(sLayer, item, boxX, boxY, boxW, boxH, cx, cy, coverScale);
            if (enabled === false) {
                sLayer.enabled = false;
            }
            return sLayer;
        }

        // Editorial HUD PNG overlay animated identically to editorialHudOverlayAndWipe in render-promo-video.mjs
        function addHudOverlay(layerName, pngName, inT, outT) {
            var item = hudItems[pngName];
            if (!item) return null;
            var hLayer = comp.layers.add(item);
            hLayer.name = layerName;
            hLayer.inPoint = inT;
            hLayer.outPoint = outT;

            var p = hLayer.property("Position");
            p.setValueAtTime(inT, [W / 2, H / 2 + 42]);
            p.setValueAtTime(inT + 0.44, [W / 2, H / 2]);
            applyEditorialBezier(p);

            var op = hLayer.property("Opacity");
            op.setValueAtTime(inT, 0);
            op.setValueAtTime(inT + 0.22, 100);
            op.setValueAtTime(outT - 0.22, 100);
            op.setValueAtTime(outT, 0);
            return hLayer;
        }

        // Optional Native Editable Helpers (created with enabled=false so HUD PNG stays primary)
        function addEditableRule(name, x, y, w, h, color, inT, outT, fromLeft) {
            var rule = comp.layers.addSolid(color, "[Editable] " + name, w, h, 1.0, DUR);
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
            sc.setValueAtTime(inT + 0.44, [100, 100]);
            sc.setValueAtTime(outT - 0.22, [100, 100]);
            sc.setValueAtTime(outT, [0, 100]);
            applyEditorialBezier(sc);
            rule.enabled = false;
            return rule;
        }

        function addEditablePanel(name, x, y, w, h, color, inT, outT, maxOp) {
            var panel = comp.layers.addSolid(color, "[Editable] " + name, w, h, 1.0, DUR);
            panel.inPoint = inT;
            panel.outPoint = outT;
            panel.property("Position").setValue([x, y]);
            var op = panel.property("Opacity");
            var peak = maxOp || 94;
            op.setValueAtTime(inT, 0);
            op.setValueAtTime(inT + 0.22, peak);
            op.setValueAtTime(outT - 0.22, peak);
            op.setValueAtTime(outT, 0);
            panel.enabled = false;
            return panel;
        }

        function addEditableText(label, str, size, color, pos, inT, outT, justify, isMono, isOutline) {
            var tl = comp.layers.addText(str);
            tl.name = "[Editable Native Text] " + label;
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
            p.setValueAtTime(inT, [pos[0], pos[1] + 42]);
            p.setValueAtTime(inT + 0.44, [pos[0], pos[1]]);
            applyEditorialBezier(p);

            var op = tl.property("Opacity");
            op.setValueAtTime(inT, 0);
            op.setValueAtTime(inT + 0.22, 100);
            op.setValueAtTime(outT - 0.22, 100);
            op.setValueAtTime(outT, 0);
            tl.enabled = false;
            return tl;
        }

        // ===================================================================
        // BASE BACKGROUND SOLID
        // ===================================================================
        var bgSolid = comp.layers.addSolid(COL_BG, "00_BG_Obsidian_07070A", W, H, 1.0, DUR);

        // ===================================================================
        // ACT 1 (0.0s - 4.8s): 2x2 QUAD-GRID + HERO STATEMENT HUD
        // ===================================================================
        addViewportVideo("Act1_Q1_ChronoRebellion", "chrono-rebellion", 0,     0,     960, 540, 0.0, 4.8, 0.5, 82);
        addViewportVideo("Act1_Q2_BehindTheSmile", "behind-the-smile", 960,   0,     960, 540, 0.0, 4.8, 1.0, 82);
        addViewportVideo("Act1_Q3_PaperPlaneDash", "paper-dash",       0,     540,   960, 540, 0.0, 4.8, 0.5, 82);
        addViewportVideo("Act1_Q4_Voxelcraft3D",   "voxelcraft",       960,   540,   960, 540, 0.0, 4.8, 1.0, 82);
        addHudOverlay("Act1_HUD_HeroStatement", "hud_scene1_intro.png", 0.0, 4.8);

        addEditablePanel("Act1_Backdrop", W / 2, H / 2, 1240, 500, COL_ELEV, 0.0, 4.8, 92);
        addEditableText("Act1_Name", "SYED MUHAMMAD AHMAD", 74, COL_FG, [388, 415], 0.0, 4.8, ParagraphJustification.LEFT_JUSTIFY, false, false);
        addEditableText("Act1_Role", "GAME & XR DEVELOPER", 74, COL_ACCENT, [388, 505], 0.0, 4.8, ParagraphJustification.LEFT_JUSTIFY, false, true);
        addEditableText("Act1_Sub", "INTERACTIVE 3D ARCHITECT.", 56, COL_FG, [388, 595], 0.0, 4.8, ParagraphJustification.LEFT_JUSTIFY, false, false);

        // ===================================================================
        // ACT 2 (4.8s - 10.2s): 001 CHRONO REBELLION
        // ===================================================================
        addFullScreenVideo("Act2_ChronoRebellion_FS", "chrono-rebellion", 4.8, 10.2, 2.0);
        addHudOverlay("Act2_HUD_Chrono", "hud_scene2_chrono.png", 4.8, 10.2);

        addEditableText("Act2_Title", "CHRONO REBELLION", 48, COL_FG, [228, 815], 4.8, 10.2, ParagraphJustification.LEFT_JUSTIFY, false, false);
        addEditableText("Act2_Sub", "Third-person and first-person sci-fi shooter featuring time-manipulation mechanics, custom HUD, and HDRP combat.", 20, COL_MUTED, [228, 868], 4.8, 10.2, ParagraphJustification.LEFT_JUSTIFY, false, false);

        // ===================================================================
        // ACT 3 (10.2s - 15.6s): 002 BEHIND THE SMILE
        // ===================================================================
        addFullScreenVideo("Act3_BehindTheSmile_FS", "behind-the-smile", 10.2, 15.6, 2.0);
        addHudOverlay("Act3_HUD_Smile", "hud_scene3_smile.png", 10.2, 15.6);

        addEditableText("Act3_Title", "BEHIND THE SMILE", 48, COL_FG, [228, 815], 10.2, 15.6, ParagraphJustification.LEFT_JUSTIFY, false, false);
        addEditableText("Act3_Sub", "Narrative-driven 3D exploration game built in 48 hours at Global Game Jam 2026 around the theme 'Masks'.", 20, COL_MUTED, [228, 868], 10.2, 15.6, ParagraphJustification.LEFT_JUSTIFY, false, false);

        // ===================================================================
        // ACT 4 (15.6s - 21.0s): 003 x 006 DUAL ENGINE SPLIT-SCREEN
        // ===================================================================
        addViewportVideo("Act4_Left_PaperPlaneDash", "paper-dash", 0,   0, 960, 1080, 15.6, 21.0, 1.5, 100);
        addViewportVideo("Act4_Right_PacMan",        "pac-man",    960, 0, 960, 1080, 15.6, 21.0, 1.0, 100);
        addHudOverlay("Act4_HUD_DualSplit", "hud_scene4_dual.png", 15.6, 21.0);

        addEditableText("Act4_LeftTitle", "PAPER PLANE DASH", 42, COL_FG, [76, 835], 15.6, 21.0, ParagraphJustification.LEFT_JUSTIFY, false, false);
        addEditableText("Act4_RightTitle", "PAC-MAN (C++ / SFML)", 42, COL_FG, [1036, 835], 15.6, 21.0, ParagraphJustification.LEFT_JUSTIFY, false, false);

        // ===================================================================
        // ACT 5 (21.0s - 26.2s): 005 VOXELCRAFT 3D
        // ===================================================================
        addFullScreenVideo("Act5_Voxelcraft3D_FS", "voxelcraft", 21.0, 26.2, 2.0);
        addHudOverlay("Act5_HUD_Voxelcraft", "hud_scene5_voxel.png", 21.0, 26.2);

        addEditableText("Act5_Title", "VOXELCRAFT 3D", 48, COL_FG, [228, 815], 21.0, 26.2, ParagraphJustification.LEFT_JUSTIFY, false, false);
        addEditableText("Act5_Sub", "Voxel-based 3D sandbox engine featuring procedural terrain chunks, block placement, and raycast destruction.", 20, COL_MUTED, [228, 868], 21.0, 26.2, ParagraphJustification.LEFT_JUSTIFY, false, false);

        // ===================================================================
        // ACT 6 (26.2s - 31.8s): 004 x 007 x 008 TRIPLE XR VIEWPORT
        // ===================================================================
        addViewportVideo("Act6_Left_SolarSystemVR",    "solar-system",   0,    0,   1080, 1080, 26.2, 31.8, 1.0, 100);
        addViewportVideo("Act6_TopRight_ARMemory",     "ar-memory",      1080, 0,   840,  540,  26.2, 31.8, 1.0, 100);
        addViewportVideo("Act6_BotRight_ARFaceFilter", "ar-face-filter", 1080, 540, 840,  540,  26.2, 31.8, 1.0, 100);
        addHudOverlay("Act6_HUD_TripleXR", "hud_scene6_xr.png", 26.2, 31.8);

        addEditableText("Act6_LeftTitle", "SOLAR SYSTEM EXPLORATION (VR)", 38, COL_FG, [76, 845], 26.2, 31.8, ParagraphJustification.LEFT_JUSTIFY, false, false);
        addEditableText("Act6_TRTitle", "AR MEMORY CARD GAME  [UNITY · VUFORIA]", 26, COL_FG, [1136, 460], 26.2, 31.8, ParagraphJustification.LEFT_JUSTIFY, false, false);
        addEditableText("Act6_BRTitle", "AR FACE FILTER  [PYTHON · OPENCV · MEDIAPIPE]", 25, COL_FG, [1136, 950], 26.2, 31.8, ParagraphJustification.LEFT_JUSTIFY, false, false);

        // ===================================================================
        // ACT 7 (31.8s - 37.0s): (02) 3D CHARACTER LAB & CAPABILITIES
        // ===================================================================
        addFullScreenVideo("Act7_ChronoBackdrop_FS", "chrono-rebellion", 31.8, 37.0, 7.5);
        addStillLayer("Act7_AvatarPreview_Still", avatarItem, 696, 156, 400, 746, 31.8, 37.0, true);
        addHudOverlay("Act7_HUD_AvatarAndStack", "hud_scene7_avatar.png", 31.8, 37.0);

        addEditableText("Act7_Title", "BLENDER 5.1 3D AVATAR", 42, COL_FG, [1140, 210], 31.8, 37.0, ParagraphJustification.LEFT_JUSTIFY, false, false);
        addEditableRule("Act7_Divider", 1482, 326, 684, 1, COL_LINE, 31.8, 37.0, true);

        // ===================================================================
        // ACT 8 (37.0s - 41.6s): (01) 09 SELECTED WORKS QUAD MATRIX
        // ===================================================================
        addViewportVideo("Act8_Q1_SolarSystem",    "solar-system", 0,   0,   960, 540, 37.0, 41.6, 3.0, 100);
        addViewportVideo("Act8_Q2_PacMan",         "pac-man",      960, 0,   960, 540, 37.0, 41.6, 3.0, 100);
        addViewportVideo("Act8_Q3_ARMemory",       "ar-memory",    0,   540, 960, 540, 37.0, 41.6, 2.5, 100);
        addViewportVideo("Act8_Q4_PaperPlaneDash", "paper-dash",   960, 540, 960, 540, 37.0, 41.6, 4.0, 100);
        addHudOverlay("Act8_HUD_QuadMatrix", "hud_scene8_quad.png", 37.0, 41.6);

        addEditableText("Act8_Title", "09 SELECTED WORKS (2024–2026)", 46, COL_FG, [W / 2, H / 2 - 10], 37.0, 41.6, ParagraphJustification.CENTER_JUSTIFY, false, false);

        // ===================================================================
        // ACT 9 (41.6s - 46.8s): (04) DIRECT TRANSMISSION OUTRO
        // ===================================================================
        addViewportVideo("Act9_Q1_BehindTheSmile", "behind-the-smile", 0,   0,   960, 540, 41.6, 46.8, 4.0, 80);
        addViewportVideo("Act9_Q2_ChronoRebellion","chrono-rebellion", 960, 0,   960, 540, 41.6, 46.8, 5.0, 80);
        addViewportVideo("Act9_Q3_Voxelcraft3D",   "voxelcraft",       0,   540, 960, 540, 41.6, 46.8, 4.0, 80);
        addViewportVideo("Act9_Q4_ARFaceFilter",   "ar-face-filter",   960, 540, 960, 540, 41.6, 46.8, 2.0, 80);
        addStillLayer("Act9_Portrait_Ahmad", portraitItem, 154, 202, 340, 654, 41.6, 46.8, true);
        addStillLayer("Act9_Avatar_3D", avatarItem, 1426, 202, 340, 654, 41.6, 46.8, true);
        addHudOverlay("Act9_HUD_DirectOutro", "hud_scene9_outro.png", 41.6, 46.8);

        addEditableText("Act9_Name", "SYED MUHAMMAD AHMAD", 56, COL_FG, [W / 2, 305], 41.6, 46.8, ParagraphJustification.CENTER_JUSTIFY, false, false);
        addEditableText("Act9_Tagline", "LET'S BUILD THE NEXT WORLD.", 44, COL_FG, [W / 2, 375], 41.6, 46.8, ParagraphJustification.CENTER_JUSTIFY, false, true);

        // ===================================================================
        // AUDIO TRACK (116 BPM FUNKY CYBER GROOVE WITH FADE-IN & FADE-OUT)
        // ===================================================================
        if (audioItem) {
            var audioLayer = comp.layers.add(audioItem);
            audioLayer.name = "Audio_FunkyCyberGroove_116BPM";
            audioLayer.startTime = 0;
            audioLayer.inPoint = 0;
            audioLayer.outPoint = DUR;
            try {
                var lvl = audioLayer.property("Audio").property("Audio Levels");
                lvl.setValueAtTime(0.0, [-48, -48]);
                lvl.setValueAtTime(0.6, [0, 0]);
                lvl.setValueAtTime(44.8, [0, 0]);
                lvl.setValueAtTime(DUR, [-48, -48]);
            } catch (eVol) {}
        }

        // Move background solid to the very bottom
        bgSolid.moveToEnd();

        // Organize generated Solids into 06_Solids folder
        try {
            var defaultSolidsFolder = null;
            for (var it = app.project.numItems; it >= 1; it--) {
                var itemObj = app.project.item(it);
                if (itemObj instanceof FolderItem && itemObj.name === "Solids") {
                    defaultSolidsFolder = itemObj;
                } else if (itemObj instanceof FootageItem && itemObj.mainSource instanceof SolidSource) {
                    itemObj.parentFolder = folderSolids;
                }
            }
            if (defaultSolidsFolder && defaultSolidsFolder.numItems === 0) {
                defaultSolidsFolder.remove();
            }
        } catch (eFolder) {}

        // Open main composition in viewer and save promo.aep
        try {
            comp.openInViewer();
        } catch (eView) {}

        var aepFile = new File(videoDir.fsName + "/promo.aep");
        app.project.save(aepFile);

        writeStatus("SUCCESS: Saved editorial " + aepFile.fsName + " (" + comp.name + ", " + DUR + "s, " + comp.numLayers + " layers)");
    } catch (err) {
        writeStatus("ERROR: " + err.toString() + " (line " + err.line + ")");
    } finally {
        app.endSuppressDialogs(false);
        app.quit();
    }
})();
