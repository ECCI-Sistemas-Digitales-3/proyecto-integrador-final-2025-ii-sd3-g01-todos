/*
 * Se requiere que imprima RGB | CMYK
 * Espera msg.payload como string tipo "#RRGGBB"
 */

// 1. OBTENER Y VALIDAR HEX
let hex = String(msg.payload || "").trim();
if (!/^#?[0-9a-fA-F]{6}$/.test(hex)) {
  node.warn("Formato HEX inválido: " + hex);
  return null;
}
if (hex[0] == = '#')
  hex = hex.slice(1);

// 2. CONVERTIR HEX A RGB (0-255)
const r = parseInt(hex.slice(0, 2), 16);
const g = parseInt(hex.slice(2, 4), 16);
const b = parseInt(hex.slice(4, 6), 16);

// 3. CONVERTIR RGB A CMYK (0-100)

// Normalizar RGB (0-1)
const rN = r / 255;
const gN = g / 255;
const bN = b / 255;

// Calcular K (Key/Black)
const k = 1 - Math.max(rN, gN, bN);

// Manejar división por cero (si K=1, el color es negro puro)
let c, m, y;
if (k == = 1) {
  c = 0;
  m = 0;
  y = 0;
} else {
  // Calcular C, M, Y
  c = (1 - rN - k) / (1 - k);
  m = (1 - gN - k) / (1 - k);
  y = (1 - bN - k) / (1 - k);
}

// Convertir a porcentaje (0-100) y redondear
const cP = Math.round(c * 100);
const mP = Math.round(m * 100);
const yP = Math.round(y * 100);
const kP = Math.round(k * 100);

// 4. FORMATEAR SALIDAS

// Mostramos RGB y CMYK en la UI
msg.payload = `RGB : ${r}, ${g}, ${b} | CMYK : ${cP} %, ${mP} %, ${yP} %,
    ${kP} %`;

// Guardamos objetos para usos futuros
msg.rgb = {r, g, b};
msg.cmyk = {c : cP, m : mP, y : yP, k : kP};

// Para archivo: agregamos timestamp y CSV simple (con RGB y CMYK)
const ts = new Date().toISOString();
msg.filePayload = `${ts};
${r};
${g};
${b};
${cP};
${mP};
${yP};
$ { kP }
`;

return [ msg ];