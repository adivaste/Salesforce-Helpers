// ==UserScript==
// @name         QR Code Scanner and Link Opener (Improved)
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Scans for QR codes on the page, supports multiple codes, and opens selected links using a shortcut key.
// @author       You
// @match        *://*/*
// @grant        none
// @require      https://unpkg.com/jsqr@1.4.0/dist/jsQR.js
// ==/UserScript==

(function() {
    'use strict';

    // Array to store all detected QR code data (URLs)
    let qrCodes = [];
    // Create a canvas element for image processing
    let canvas = document.createElement('canvas');
    let context = canvas.getContext('2d');

    // Customizable shortcut configuration (Ctrl+Shift+Q by default)
    const shortcut = { ctrl: true, shift: true, key: 'Q' };

    // Helper function to process an image element
    function processImage(img) {
        // Skip processing if the image has already been checked
        if (img.dataset.qrProcessed) return;

        // Use natural dimensions for best resolution
        const width = img.naturalWidth;
        const height = img.naturalHeight;
        if (width === 0 || height === 0) return; // Skip if image is not properly loaded

        canvas.width = width;
        canvas.height = height;
        context.drawImage(img, 0, 0, width, height);

        try {
            let imageData = context.getImageData(0, 0, width, height);
            let code = jsQR(imageData.data, width, height);
            if (code) {
                qrCodes.push(code.data);
                console.log('QR Code found:', code.data);
                // Visual feedback: add a red border to images where a QR code was detected
                img.style.border = "2px solid red";
            }
        } catch (error) {
            console.error('Error processing image:', error);
        }

        // Mark the image as processed to avoid duplicate work
        img.dataset.qrProcessed = "true";
    }

    // Function to scan all images on the page
    function scanForQrCodes() {
        const images = document.querySelectorAll('img');
        images.forEach(img => processImage(img));
    }

    // MutationObserver to detect newly added images dynamically
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                // If the added node is an image, process it directly
                if (node.tagName === 'IMG') {
                    processImage(node);
                }
                // Otherwise, if the node contains images, process all of them
                else if (node.nodeType === Node.ELEMENT_NODE) {
                    const imgs = node.querySelectorAll('img');
                    imgs.forEach(img => processImage(img));
                }
            });
        });
    });

    // Start observing the document body for changes
    observer.observe(document.body, { childList: true, subtree: true });

    // Function to open a QR code link
    // If multiple QR codes exist, prompt the user to select one.
    function openQrCodeLink() {
        if (qrCodes.length > 0) {
            if (qrCodes.length === 1) {
                // Open directly if there's only one QR code
                window.open(qrCodes[0], '_blank');
            } else {
                // List all QR codes and let the user choose which one to open
                let message = "Multiple QR Codes found. Choose one:\n";
                qrCodes.forEach((code, index) => {
                    message += `${index + 1}: ${code}\n`;
                });
                message += "Enter the number of the link to open:";
                let choice = prompt(message);
                let index = parseInt(choice, 10) - 1;
                if (index >= 0 && index < qrCodes.length) {
                    window.open(qrCodes[index], '_blank');
                } else {
                    alert("Invalid selection.");
                }
            }
        } else {
            alert("No QR code found yet. Please wait for the page to load or refresh.");
        }
    }

    // Listen for the customizable shortcut key (default: Ctrl+Shift+Q)
    document.addEventListener('keydown', function(event) {
        if (event.ctrlKey === shortcut.ctrl &&
            event.shiftKey === shortcut.shift &&
            event.key.toUpperCase() === shortcut.key) {
            openQrCodeLink();
        }
    });

    // Initial scan once the page has fully loaded
    window.addEventListener('load', scanForQrCodes);

    // Optionally, you could also set up periodic scanning if needed:
    // setInterval(scanForQrCodes, 5000);
})();
