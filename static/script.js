document.addEventListener("DOMContentLoaded", function () {
    startScanner();
    loadProducts();
    setupCamera();
});

// ฟังก์ชันเปิด/ปิดกล้อง
let cameraStream;
function setupCamera() {
    let cameraStreamElement = document.getElementById("camera-stream");
    let captureButton = document.getElementById("capture-photo");
    let searchButton = document.getElementById("search-lens");
    let previewImage = document.getElementById("preview-image");
    let openCameraButton = document.getElementById("open-camera");
    let closeCameraButton = document.getElementById("close-camera");

    // เปิดกล้อง
    openCameraButton.addEventListener("click", function () {
        navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
            .then(function (stream) {
                cameraStream = stream;
                cameraStreamElement.srcObject = stream;
                cameraStreamElement.style.display = "block";
                captureButton.style.display = "inline-block";
                searchButton.style.display = "inline-block";
                closeCameraButton.style.display = "inline-block";
                openCameraButton.style.display = "none";
            })
            .catch(function (err) {
                console.error("Camera access error:", err);
                alert("Unable to access camera. Please check your browser permissions.");
            });
    });

    // ปิดกล้อง
    closeCameraButton.addEventListener("click", function () {
        if (cameraStream) {
            let tracks = cameraStream.getTracks();
            tracks.forEach(track => track.stop());
        }
        cameraStreamElement.style.display = "none";
        captureButton.style.display = "none";
        searchButton.style.display = "none";
        closeCameraButton.style.display = "none";
        openCameraButton.style.display = "inline-block";
    });

    // ถ่ายรูปจากกล้อง
    captureButton.addEventListener("click", function () {
        let canvas = document.getElementById("captured-image");
        let context = canvas.getContext("2d");
        canvas.width = cameraStreamElement.videoWidth;
        canvas.height = cameraStreamElement.videoHeight;
        context.drawImage(cameraStreamElement, 0, 0, canvas.width, canvas.height);

        // แสดงภาพตัวอย่าง
        previewImage.src = canvas.toDataURL("image/png");
        previewImage.style.display = "block";
    });

    // ค้นหาภาพผ่าน Google Lens
    searchButton.addEventListener("click", function () {
        if (previewImage.src) {
            let googleLensUrl = `https://lens.google.com/uploadbyurl?url=${previewImage.src}`;
            window.open(googleLensUrl, "_blank");
        } else {
            alert("Please capture an image first.");
        }
    });
}

// ฟังก์ชันโหลดสินค้า
function loadProducts() {
    fetch("/api/products")
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById("product-list");
            list.innerHTML = "";
            data.forEach(product => {
                let li = document.createElement("li");
                li.className = "list-group-item";
                li.innerHTML = `${product.name} - ${product.barcode} <a href="/generate/${product.barcode}" class="btn btn-sm btn-success">Download Barcode</a>`;
                list.appendChild(li);
            });
        });
}

// ฟังก์ชันเปิด QuaggaJS Scanner
function startScanner() {
    Quagga.init({
        inputStream: {
            name: "Live",
            type: "LiveStream",
            target: document.getElementById("scanner"),
        },
        decoder: {
            readers: ["ean_reader", "upc_reader", "code_128_reader"]
        }
    }, function (err) {
        if (err) {
            console.error(err);
            return;
        }
        Quagga.start();
    });

    Quagga.onDetected(function (result) {
        document.getElementById("barcode-result").innerText = result.codeResult.code;
    });
}
