// Probe: list output module templates, fonts, and check file write permission.
(function () {
    var out = new File(File($.fileName).parent.fsName + "/probe_out.txt");
    var lines = [];
    lines.push("AE version: " + app.version);
    var c = app.project.items.addComp("probe", 1920, 1080, 1, 2, 30);
    var rq = app.project.renderQueue.items.add(c);
    var t = rq.outputModule(1).templates;
    lines.push("OM templates:");
    for (var i = 0; i < t.length; i++) lines.push("  " + t[i]);
    var rs = rq.templates;
    lines.push("RS templates:");
    for (var j = 0; j < rs.length; j++) lines.push("  " + rs[j]);
    try {
        var s = rq.outputModule(1).getSettings(GetSettingsFormat.STRING_SETTABLE);
        for (var k in s) lines.push("OMset " + k + " = " + s[k]);
    } catch (e) { lines.push("getSettings err " + e); }
    try {
        var f = app.fonts.getFontsByFamilyNameAndStyleName("Bahnschrift", "Bold Condensed");
        lines.push("Bahnschrift BoldCond: " + (f && f.length ? f[0].postScriptName : "none"));
        var fam = app.fonts.allFonts;
        for (var a = 0; a < fam.length; a++) {
            var g = fam[a];
            for (var b = 0; b < g.length; b++) {
                if (g[b].familyName.indexOf("Bahnschrift") >= 0 || g[b].familyName.indexOf("Consolas") >= 0)
                    lines.push("  font: " + g[b].familyName + " / " + g[b].styleName + " / " + g[b].postScriptName);
            }
        }
    } catch (e2) { lines.push("fonts err " + e2); }
    out.encoding = "UTF-8";
    out.open("w");
    out.write(lines.join("\n"));
    out.close();
    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    app.quit();
})();
