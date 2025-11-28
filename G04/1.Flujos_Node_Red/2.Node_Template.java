<div style="text-align:center;">
    <h3>Selecciona un punto de la imagen</h3>
    <canvas id="canvas" width="640" height="480" style="border:1px solid #000;"></canvas>
    <p id="colorInfo">Haz clic en un punto de la imagen</p>
</div>

<script>
    (function(scope) {
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    const colorInfo = document.getElementById("colorInfo");
    let img = new Image();

    scope.$watch('msg.payload', function(data) {
        if (!data) return;
        img = new Image();
        img.onload = function() {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        };
        img.src = data;
    });

    // NUEVA función: convierte r,g,b (0..255) a CMYKW normalizados que sumen 100
    function rgbToCMYKW(r, g, b) {
        // normalizamos 0..1
        let R = r / 255;
        let G = g / 255;
        let B = b / 255;

        // CMY base (sustractivo simple)
        let C = 1 - R;
        let M = 1 - G;
        let Y = 1 - B;

        // K = min(C,M,Y) (parte negra que se puede extraer)
        let K = Math.min(C, M, Y);

        // Partes residuales de CMY después de extraer K
        let Cr = Math.max(0, C - K);
        let Mr = Math.max(0, M - K);
        let Yr = Math.max(0, Y - K);

        // W (blanco) — lo que sobra hasta 1 si la suma de componentes es < 1
        // Calculamos suma física sin normalizar
        let rawSum = Cr + Mr + Yr + K;
        let W = 0;
        if (rawSum < 1) {
            W = 1 - rawSum;
        } else {
            W = 0;
        }

        // Ahora normalizamos para que C+M+Y+K+W = 1 (siempre)
        let total = Cr + Mr + Yr + K + W;
        if (total <= 0) total = 1; // seguridad

        let Cn = Cr / total;
        let Mn = Mr / total;
        let Yn = Yr / total;
        let Kn = K  / total;
        let Wn = W  / total;

        // convertir a porcentajes enteros
        let Cperc = Math.round(Cn * 100);
        let Mperc = Math.round(Mn * 100);
        let Yperc = Math.round(Yn * 100);
        let Kperc = Math.round(Kn * 100);
        let Wperc = Math.round(Wn * 100);

        // ajustar redondeo para que sumen exactamente 100
        let arr = [
            {k:'C', v:Cperc},
            {k:'M', v:Mperc},
            {k:'Y', v:Yperc},
            {k:'K', v:Kperc},
            {k:'W', v:Wperc}
        ];
        let sum = Cperc + Mperc + Yperc + Kperc + Wperc;
        let diff = 100 - sum;

        if (diff !== 0) {
            // encontrar el componente con mayor valor (para ajustar ahí)
            arr.sort((a,b) => b.v - a.v);
            arr[0].v += diff; // puede ser negativo o positivo
        }

        // reconstruir objeto final
        let result = {
            C: arr.find(x=>x.k==='C').v,
            M: arr.find(x=>x.k==='M').v,
            Y: arr.find(x=>x.k==='Y').v,
            K: arr.find(x=>x.k==='K').v,
            W: arr.find(x=>x.k==='W').v
        };

        return result;
    }

    // Detectar clic
    canvas.addEventListener("click", function(event) {
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const pixel = ctx.getImageData(x, y, 1, 1).data;
        const r = pixel[0];
        const g = pixel[1];
        const b = pixel[2];

        const rgb = `rgb(${r}, ${g}, ${b})`;
        const hex = "#" + ((1 << 24) + (r << 16) + (g << 8) + b)
            .toString(16).slice(1).toUpperCase();

        const cmykw = rgbToCMYKW(r, g, b);

        const texto = `Coordenadas: (${Math.round(x)},${Math.round(y)}) - ${rgb} - ${hex} - C:${cmykw.C} M:${cmykw.M} Y:${cmykw.Y} K:${cmykw.K} W:${cmykw.W}`;

        colorInfo.innerText = texto;

        // Enviar a Node-RED (payload con todo)
        scope.send({
            payload: {
                x: Math.round(x),
                y: Math.round(y),
                rgb: [r, g, b],
                hex: hex,
                C: cmykw.C,
                M: cmykw.M,
                Y: cmykw.Y,
                K: cmykw.K,
                W: cmykw.W,
                texto: texto
            }
        });
    });

})(scope);
</script>