// Añade una marca de tiempo para forzar la recarga de la imagen
// Apuntamos a /test.png, como pediste.
msg.url = "/test.png?t=" + Date.now();
// img.src = '/static/test.png?' + new Date().getTime();
return msg;