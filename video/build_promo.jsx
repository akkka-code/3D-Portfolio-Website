/*
 * build_promo.jsx — ExtendScript for Adobe After Effects 2026
 * Builds the 46-second promotional video for Syed Muhammad Ahmad (AKKA)
 * from content/profile.json, imports the synthesized CC0 synthwave soundtrack
 * (video/music/promo_music.wav), and saves video/promo.aep.
 *
 * Run via:
 *   "C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\AfterFX.exe" -noui -r "d:\Projects v1\Portfolio Website\video\build_promo.jsx"
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

        // Read content/profile.json
        var profileFile = new File(rootDir.fsName + "/content/profile.json");
        var profile = {
            name: "SYED MUHAMMAD AHMAD",
            handle: "AKKA",
            role: "Game Developer · Game Programmer · Graphic Designer",
            tagline: "Building immersive games and interactive 3D worlds with Unity, Unreal Engine 5 & AI.",
            email: "ahmedakka765@gmail.com",
            location: "NED University · Karachi, Pakistan"
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
        var DUR = 46.0;

        var comp = app.project.items.addComp("PROMO_MAIN", W, H, 1.0, DUR, FPS);
        comp.bgColor = [0.02, 0.025, 0.045];

        // Colors
        var COL_BG = [0.025, 0.03, 0.055];
        var COL_CARD = [0.055, 0.075, 0.13];
        var COL_CYAN = [0.0, 0.90, 1.0];
        var COL_MAGENTA = [1.0, 0.17, 0.84];
        var COL_YELLOW = [0.99, 0.93, 0.04];
        var COL_WHITE = [0.96, 0.98, 1.0];
        var COL_MUTED = [0.62, 0.72, 0.84];

        // Import synthesized soundtrack if available
        var wavFile = new File(videoDir.fsName + "/music/promo_music.wav");
        if (wavFile.exists) {
            var importOpts = new ImportOptions(wavFile);
            var audioItem = app.project.importFile(importOpts);
            var audioLayer = comp.layers.add(audioItem);
            audioLayer.startTime = 0;
        }

        // Import gameplay footage clips if available for PiP background showcase
        var gpFolder = new Folder(rootDir.fsName + "/public/video/projects");
        var gpSlugs = ["chrono-rebellion", "behind-the-smile", "paper-dash", "solar-system"];
        var gpItems = {};
        for (var g = 0; g < gpSlugs.length; g++) {
            var gf = new File(gpFolder.fsName + "/" + gpSlugs[g] + ".mp4");
            if (gf.exists) {
                try {
                    gpItems[gpSlugs[g]] = app.project.importFile(new ImportOptions(gf));
                } catch (eImp) {}
            }
        }

        // Import FilmBro VFX Assets Pack overlays (Glitch, HUD, Particles, Sparks)
        var vfxRoot = new Folder("C:/Users/Syed Muhammad Ahmad/Downloads/Full Bundle Free VFX Assets Pack");
        var vfxPaths = [
            "FilmBro_10 Glitch Elements/Cyperpunk Style Glitch Element_01_[FulHD].mp4",
            "FilmBro_10 HUD Elements/Hollywood HUD Pack_Custom frame 1_[FullHD].mp4",
            "FilmBro_10 Real Particles/Particles_01 [FullHD].mp4",
            "FilmBro_5 Sparks/Spark 01_[FullHD].mov"
        ];
        for (var vIdx = 0; vIdx < vfxPaths.length; vIdx++) {
            var vf = new File(vfxRoot.fsName + "/" + vfxPaths[vIdx]);
            if (vf.exists) {
                try {
                    var vfxItem = app.project.importFile(new ImportOptions(vf));
                    var vfxLayer = comp.layers.add(vfxItem);
                    vfxLayer.audioEnabled = false;
                    vfxLayer.blendingMode = BlendingMode.SCREEN;
                    vfxLayer.property("Opacity").setValue(35);
                } catch (eVfx) {}
            }
        }

        // Background Solid + subtle vignette & scanlines
        var bgSolid = comp.layers.addSolid(COL_BG, "BG_Navy", W, H, 1.0, DUR);
        bgSolid.moveToEnd();

        // Top & Bottom Cyberpunk HUD Bars (always visible)
        var topBar = comp.layers.addSolid(COL_CYAN, "HUD_TopBar", W, 4, 1.0, DUR);
        topBar.property("Position").setValue([W / 2, 42]);
        topBar.property("Opacity").setValue(65);

        var botBar = comp.layers.addSolid(COL_MAGENTA, "HUD_BottomBar", W, 4, 1.0, DUR);
        botBar.property("Position").setValue([W / 2, H - 42]);
        botBar.property("Opacity").setValue(65);

        // Helper: add styled text with fade & slide-in/out keyframes
        function addText(str, size, color, pos, inT, outT, justify) {
            var tl = comp.layers.addText(str);
            tl.inPoint = inT;
            tl.outPoint = outT;
            var prop = tl.property("Source Text");
            var doc = prop.value;
            doc.fontSize = size;
            doc.fillColor = color;
            doc.applyFill = true;
            doc.applyStroke = false;
            try {
                doc.font = "Bahnschrift";
            } catch (eFont) {}
            doc.justification = justify || ParagraphJustification.CENTER_JUSTIFY;
            prop.setValue(doc);

            var p = tl.property("Position");
            var op = tl.property("Opacity");
            var fade = 0.45;
            p.setValueAtTime(inT, [pos[0], pos[1] + 28]);
            p.setValueAtTime(inT + fade, [pos[0], pos[1]]);
            p.setValueAtTime(outT - fade, [pos[0], pos[1]]);
            p.setValueAtTime(outT, [pos[0], pos[1] - 20]);

            op.setValueAtTime(inT, 0);
            op.setValueAtTime(inT + fade, 100);
            op.setValueAtTime(outT - fade, 100);
            op.setValueAtTime(outT, 0);
            return tl;
        }

        function addCard(name, w, h, color, pos, inT, outT, maxOp) {
            var sl = comp.layers.addSolid(color, name, w, h, 1.0, DUR);
            sl.inPoint = inT;
            sl.outPoint = outT;
            sl.property("Position").setValue(pos);
            var op = sl.property("Opacity");
            var peak = maxOp || 88;
            op.setValueAtTime(inT, 0);
            op.setValueAtTime(inT + 0.35, peak);
            op.setValueAtTime(outT - 0.35, peak);
            op.setValueAtTime(outT, 0);
            return sl;
        }

        // Persistent HUD corner text
        var hudLeft = addText("PORTFOLIO // SYED MUHAMMAD AHMAD [AKKA]", 20, COL_CYAN, [60, 28], 0, DUR, ParagraphJustification.LEFT_JUSTIFY);
        var hudRight = addText("NED UNIVERSITY · GAMING & ANIMATION · 2026", 20, COL_MUTED, [W - 60, 28], 0, DUR, ParagraphJustification.RIGHT_JUSTIFY);

        // ===================================================================
        // SCENE 1 (0.0s - 4.8s): Cyber Boot Sequence
        // ===================================================================
        addText("// INITIALIZING NEURAL 3D ENGINE · WEBGPU + TSL", 26, COL_CYAN, [W / 2, H / 2 - 110], 0.1, 4.7);
        addCard("LogoBox", 220, 110, COL_CYAN, [W / 2, H / 2 - 5], 0.3, 4.7, 22);
        addText("AKKA", 78, COL_WHITE, [W / 2, H / 2 + 22], 0.3, 4.7);
        addText("INTERACTIVE 3D PORTFOLIO · AI RAG ASSISTANT · GAME SHOWCASE", 24, COL_MAGENTA, [W / 2, H / 2 + 125], 0.6, 4.7);

        // ===================================================================
        // SCENE 2 (4.8s - 12.0s): Developer Identity Reveal
        // ===================================================================
        addText("HELLO WORLD, I AM", 26, COL_CYAN, [W / 2, 310], 4.8, 12.0);
        addText((profile.name || "SYED MUHAMMAD AHMAD").toUpperCase(), 88, COL_WHITE, [W / 2, 430], 5.0, 12.0);
        addCard("RoleAccent", 980, 56, COL_MAGENTA, [W / 2, 520], 5.2, 12.0, 28);
        addText("GAME DEVELOPER  ·  GAME PROGRAMMER  ·  GRAPHIC DESIGNER", 32, COL_YELLOW, [W / 2, 532], 5.3, 12.0);
        addText("BS CS & IT (Gaming & Animation) · NED University of Engineering & Technology", 27, COL_MUTED, [W / 2, 635], 5.6, 12.0);
        addText("Game Development Intern @ Aerox ERP", 28, COL_CYAN, [W / 2, 695], 5.9, 12.0);

        // ===================================================================
        // SCENE 3 (12.0s - 21.6s): Technical Arsenal & Game Engines
        // ===================================================================
        addText("01 // TECHNICAL ARSENAL & ENGINES", 44, COL_CYAN, [W / 2, 165], 12.0, 21.6);
        var skillBoxes = [
            { title: "GAME ENGINES", items: "Unity (HDRP / URP) · Unreal Engine 5 · Blueprints · SFML", x: 510, y: 360, c: COL_CYAN },
            { title: "PROGRAMMING", items: "C# · C++ · C · Python · Data Structures & QuadTrees", x: 1410, y: 360, c: COL_MAGENTA },
            { title: "XR (AR / VR)", items: "OpenXR · XR Interaction Toolkit · Vuforia · OpenCV · MediaPipe", x: 510, y: 580, c: COL_YELLOW },
            { title: "3D, DESIGN & AI", items: "Blender 3D · Three.js WebGPU · Photoshop & Illustrator · RAG AI", x: 1410, y: 580, c: COL_CYAN }
        ];
        for (var s = 0; s < skillBoxes.length; s++) {
            var sb = skillBoxes[s];
            var st = 12.3 + s * 0.35;
            addCard("SkillCard_" + s, 820, 165, COL_CARD, [sb.x, sb.y], st, 21.6, 88);
            addCard("SkillBar_" + s, 820, 5, sb.c, [sb.x, sb.y - 80], st, 21.6, 95);
            addText(sb.title, 30, sb.c, [sb.x, sb.y - 25], st + 0.1, 21.6);
            addText(sb.items, 23, COL_WHITE, [sb.x, sb.y + 32], st + 0.2, 21.6);
        }
        addText("8+ PLAYABLE GAMES  ·  AR/VR EXPERIENCES  ·  CUSTOM 3D AVATAR", 26, COL_MUTED, [W / 2, 830], 13.8, 21.6);

        // ===================================================================
        // SCENE 4 (21.6s - 33.6s): Featured Game Projects Showcase (4 x 3.0s)
        // ===================================================================
        var featured = [
            {
                slug: "chrono-rebellion",
                tag: "FEATURED PROJECT 01 // SCI-FI FPS & TPS SHOOTER",
                title: "CHRONO REBELLION",
                tech: "Unity · C# · High Definition Render Pipeline (HDRP)",
                desc: "Time-manipulation combat mechanics, weapon HUD, and hybrid 1st/3rd-person controls."
            },
            {
                slug: "behind-the-smile",
                tag: "FEATURED PROJECT 02 // GLOBAL GAME JAM 2026 (48H)",
                title: "BEHIND THE SMILE",
                tech: "Unity · C# · Narrative 3D Game · Theme: 'Masks'",
                desc: "Interactive 3D narrative game built in 48 hours featuring custom UI and core systems."
            },
            {
                slug: "paper-dash",
                tag: "FEATURED PROJECT 03 // PROCEDURAL ENDLESS RUNNER",
                title: "PAPER PLANE DASH",
                tech: "Unreal Engine 5 · Blueprints · Procedural Generation",
                desc: "Dynamic lane switching, procedural obstacle spawning, and responsive flight physics."
            },
            {
                slug: "solar-system",
                tag: "FEATURED PROJECT 04 // IMMERSIVE VR EDUCATION",
                title: "SOLAR SYSTEM VR",
                tech: "Unity · OpenXR · XR Interaction Toolkit · World-Space UI",
                desc: "VR teleportation locomotion and interactive planetary exploration in virtual reality."
            }
        ];

        for (var pIdx = 0; pIdx < featured.length; pIdx++) {
            var fp = featured[pIdx];
            var pIn = 21.6 + pIdx * 3.0;
            var pOut = pIn + 3.0;

            // If gameplay video item exists, place it on the right half
            if (gpItems[fp.slug]) {
                var vLayer = comp.layers.add(gpItems[fp.slug]);
                vLayer.audioEnabled = false;
                vLayer.startTime = pIn;
                vLayer.inPoint = pIn;
                vLayer.outPoint = pOut;
                vLayer.property("Position").setValue([1340, 540]);
                vLayer.property("Scale").setValue([72, 72]);
                var vOp = vLayer.property("Opacity");
                vOp.setValueAtTime(pIn, 0);
                vOp.setValueAtTime(pIn + 0.3, 95);
                vOp.setValueAtTime(pOut - 0.3, 95);
                vOp.setValueAtTime(pOut, 0);
            }

            addCard("ProjCard_" + pIdx, 760, 460, COL_CARD, [470, 540], pIn, pOut, 92);
            addCard("ProjAccent_" + pIdx, 8, 460, COL_CYAN, [94, 540], pIn, pOut, 100);
            addText(fp.tag, 22, COL_MAGENTA, [130, 375], pIn + 0.05, pOut, ParagraphJustification.LEFT_JUSTIFY);
            addText(fp.title, 58, COL_WHITE, [130, 465], pIn + 0.1, pOut, ParagraphJustification.LEFT_JUSTIFY);
            addText(fp.tech, 25, COL_CYAN, [130, 540], pIn + 0.15, pOut, ParagraphJustification.LEFT_JUSTIFY);
            addText(fp.desc, 22, COL_MUTED, [130, 635], pIn + 0.2, pOut, ParagraphJustification.LEFT_JUSTIFY);
        }

        // ===================================================================
        // SCENE 5 (33.6s - 38.4s): More Games, Certifications & Achievements
        // ===================================================================
        addText("03 // MORE PROJECTS & CERTIFICATIONS", 44, COL_CYAN, [W / 2, 175], 33.6, 38.4);
        addCard("MoreCard1", 1620, 170, COL_CARD, [W / 2, 370], 33.8, 38.4, 88);
        addText("MORE PLAYABLE DEMOS IN THIS PORTFOLIO", 26, COL_YELLOW, [W / 2, 325], 33.9, 38.4);
        addText("Voxelcraft 3D Sandbox  ·  Pac-Man (C++ / SFML / QuadTrees)  ·  AR Memory Card (Vuforia)  ·  AR Face Filter (OpenCV & MediaPipe)", 25, COL_WHITE, [W / 2, 395], 34.0, 38.4);

        addCard("MoreCard2", 1620, 190, COL_CARD, [W / 2, 620], 34.2, 38.4, 88);
        addText("CERTIFICATIONS & HONORS", 26, COL_MAGENTA, [W / 2, 565], 34.3, 38.4);
        addText("Unreal Engine (CEGA)  ·  Pre-Production & Post-Production (CEGA)  ·  Google AI (Coursera)  ·  Global Game Jam 2026", 26, COL_CYAN, [W / 2, 640], 34.4, 38.4);

        // ===================================================================
        // SCENE 6 (38.4s - 46.0s): Call to Action & Outro
        // ===================================================================
        addText("EXPLORE THE INTERACTIVE 3D CYBERPUNK ALLEY", 34, COL_CYAN, [W / 2, 290], 38.4, 45.6);
        addText("SYED MUHAMMAD AHMAD", 76, COL_WHITE, [W / 2, 405], 38.6, 45.6);
        addCard("CtaBanner", 1180, 68, COL_CYAN, [W / 2, 510], 38.8, 45.6, 25);
        addText("WALK THE 3D WORLD  ·  MEET THE 3D AVATAR  ·  ASK THE RAG AI CHATBOT", 27, COL_YELLOW, [W / 2, 520], 38.9, 45.6);
        addText("ahmedakka765@gmail.com   |   linkedin.com/in/syed-muhammad-ahmad-55b240284", 26, COL_MUTED, [W / 2, 640], 39.2, 45.6);
        addText("+92 332 2669028   ·   Karachi, Pakistan", 24, COL_MAGENTA, [W / 2, 700], 39.4, 45.6);

        // Save After Effects Project (.aep)
        var aepFile = new File(videoDir.fsName + "/promo.aep");
        app.project.save(aepFile);

        // Write status marker
        var statusFile = new File(videoDir.fsName + "/build_status.txt");
        statusFile.encoding = "UTF-8";
        if (statusFile.open("w")) {
            statusFile.write("SUCCESS: Saved " + aepFile.fsName + " (" + comp.name + ", " + DUR + "s)");
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
