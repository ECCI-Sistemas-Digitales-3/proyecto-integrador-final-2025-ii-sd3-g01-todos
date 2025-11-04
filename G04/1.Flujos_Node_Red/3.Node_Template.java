<style>
    #picker-canvas-{{$id}} { width: 100%; height: auto; cursor: crosshair; }
    #picker-info-{{$id}} { margin-top: 10px; font-family: monospace; }
    #picker-swatch-{{$id}} { display: inline-block; width: 25px; height: 25px; border: 1px solid #ccc; vertical-align: middle; margin-right: 5px; }
</style>

<canvas id="picker-canvas-{{$id}}"></canvas>
<div id="picker-info-{{$id}}">
    <span id="picker-swatch-{{$id}}"></span>
    <span id="picker-rgb-{{$id}}">(R, G, B)</span>
</div>

<script>
(function(scope) {
    // Referencias a elementos HTML
    var canvas = document.getElementById('picker-canvas-{{$id}}');
    var ctx = canvas.getContext('2d');
    var swatch = document.getElementById('picker-swatch-{{$id}}');
    var rgbText = document.getElementById('picker-rgb-{{$id}}');

    var img = new Image();
    img.crossOrigin = "Anonymous";

    function updateImage() {
        // Añadimos un timestamp para evitar problemas de caché del navegador
        img.src = '/test.png?' + new Date().getTime();
    }

    img.onload = function() {
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        ctx.drawImage(img, 0, 0, img.naturalWidth, img.naturalHeight);
        swatch.style.backgroundColor = "#fff";
        rgbText.textContent = "(R, G, B)";
    };
    
    img.onerror = function() {
        console.error("No se pudo cargar la imagen /test.png");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = "16px Arial"; ctx.fillStyle = "red";
        ctx.fillText("Error al cargar /test.png", 10, 30);
    };

    canvas.addEventListener('click', function(event) {
        var rect = canvas.getBoundingClientRect(); 
        var scaleX = canvas.width / rect.width;
        var scaleY = canvas.height / rect.height;
        
        var x = Math.floor(event.offsetX * scaleX);
        var y = Math.floor(event.offsetY * scaleY);
        
        var pixelData = ctx.getImageData(x, y, 1, 1).data;
        
        var r = pixelData[0];
        var g = pixelData[1];
        var b = pixelData[2];
        
        // Actualiza la UI del template
        var rgbString = `rgb(${r}, ${g}, ${b})`;
        swatch.style.backgroundColor = rgbString;
        rgbText.textContent = `(${r}, ${g}, ${b})  [${x}, ${y}]`;

        // ======================================================
        //              *** SECCIÓN CORREGIDA ***
        // ======================================================
        
        // 1. Creamos el OBJETO JSON que requiere el color picker
        var colorObject = {
            r: r,
            g: g,
            b: b,
            a: 1  // Añadimos el canal alfa (opacidad) fijado a 1
        };

        // 2. Creamos un nuevo objeto 'msg' con ese objeto como payload
        var newMsg = {
            payload: colorObject
        };
         
        // 3. Enviamos el mensaje por la salida del nodo
        scope.send(newMsg);
        // ======================================================
    });
    
    // Se activa cuando un mensaje ENTRA al nodo template
    scope.$watch('msg', function(msg) {
        if (msg) {
            // Asume que cualquier mensaje entrante (del botón)
            // debe refrescar la imagen.
            updateImage();
        }
    });

    // Carga la imagen una vez cuando el dashboard se inicia
    setTimeout(updateImage, 100);

})(scope);
</script>