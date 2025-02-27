// ==UserScript==
// @name         Open Salesforce Object Manager
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Open Salesforce Object Manager page with a shortcut
// @author       Aditya Vaste
// @match        *://*.my.salesforce.com/*
// @match        *://*.lightning.force.com/*
// @match        *://*.force.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Shortcut key (Ctrl + M in this example)
    document.addEventListener("keydown", function(event) {
        if (event.ctrlKey && event.key === "m") {
            
            console.log('Object Manager');
            event.preventDefault(); 
            
            const baseUrl = `${window.location.origin}/`;
            const objectManagerPath = "lightning/setup/ObjectManager/home";
            const fullUrl = baseUrl + objectManagerPath;

            window.open(fullUrl, "_blank");
        }
        if (event.ctrlKey && event.key === "b") {
            
            console.log('Flows');
            event.preventDefault();

            const baseUrl = `${window.location.origin}/`;
            const objectManagerPath = "lightning/setup/Flows/home";
            const fullUrl = baseUrl + objectManagerPath;

            window.open(fullUrl, "_blank");
        }
        if (event.ctrlKey && event.key === "k") {
            
            console.log('Dev Console');
            event.preventDefault();

            const baseUrl = `${window.location.origin}/`;
            const objectManagerPath = "_ui/common/apex/debug/ApexCSIPage";
            const fullUrl = baseUrl + objectManagerPath;

            var innerWidth = window.innerWidth;
            var innerHeight = window.innerHeight;
            var extraParams = `width=${innerWidth},height=${innerHeight}`

            window.open(fullUrl, "_blank", extraParams);
        }
    });
})();
