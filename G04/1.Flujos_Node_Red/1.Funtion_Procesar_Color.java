// espera msg.payload = {x, y, rgb:[r,g,b], hex:"#RRGGBB"}

let info = msg.payload || {};
let hex = info.hex || "#000000";
let rgb = info.rgb || [ 0, 0, 0 ];
let x = info.x;
let y = info.y;

// --------- CALCULAR CMYKW ---------
let R = (rgb[0] || 0) / 255;
let G = (rgb[1] || 0) / 255;
let B = (rgb[2] || 0) / 255;

let K = 1 - Math.max(R, G, B);
let denom = (1 - K) || 1;
let C = ((1 - R - K) / denom) || 0;
let M = ((1 - G - K) / denom) || 0;
let Y = ((1 - B - K) / denom) || 0;

// Blanco simple
let W = Math.min(R, G, B);

// Convertir a %
C = Math.round(C * 100);
M = Math.round(M * 100);
Y = Math.round(Y * 100);
K = Math.round(K * 100);
W = Math.round(W * 100);

// --------- TEXTO EXACTO QUE SE MUESTRA EN EL DASHBOARD ---------

let texto = `Coordenadas : (${x}, ${y}) - rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]}) -
                           ${hex} - C : ${C} M : ${M} Y : ${Y} K : ${K} W : $ {
  W
}
`;

// --------- Salida 1: colour picker (solo HEX) ---------
let msgColor = {payload : hex};

// --------- Salida 2: dashboard con texto completo ---------
let msgDashboard = {payload : texto};

// Devolver SOLO dos salidas como pediste
return [ msgColor, msgDashboard ];