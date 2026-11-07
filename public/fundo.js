(function () {
  const tela = document.getElementById("fundo");
  const ctx = tela.getContext("2d");
  const reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const distancia = 140;
  let largura = 0;
  let altura = 0;
  let pontos = [];
  let quadro = null;

  function criarPontos() {
    const total = Math.min(90, Math.floor((largura * altura) / 16000));
    pontos = [];
    for (let i = 0; i < total; i++) {
      pontos.push({
        x: Math.random() * largura,
        y: Math.random() * altura,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
        r: 1 + Math.random() * 1.6
      });
    }
  }

  function ajustar() {
    const escala = window.devicePixelRatio || 1;
    largura = window.innerWidth;
    altura = window.innerHeight;
    tela.width = largura * escala;
    tela.height = altura * escala;
    ctx.setTransform(escala, 0, 0, escala, 0, 0);
    criarPontos();
    desenhar();
  }

  function mover() {
    pontos.forEach((p) => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > largura) p.vx = -p.vx;
      if (p.y < 0 || p.y > altura) p.vy = -p.vy;
    });
  }

  function desenhar() {
    ctx.clearRect(0, 0, largura, altura);
    for (let i = 0; i < pontos.length; i++) {
      const a = pontos[i];
      for (let j = i + 1; j < pontos.length; j++) {
        const b = pontos[j];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        if (d < distancia) {
          ctx.strokeStyle = "rgba(110, 168, 255," + (0.22 * (1 - d / distancia)) + ")";
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }
    ctx.fillStyle = "rgba(150, 195, 255, 0.55)";
    pontos.forEach((p) => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  function animar() {
    mover();
    desenhar();
    quadro = requestAnimationFrame(animar);
  }

  function iniciar() {
    if (reduzido || quadro !== null) return;
    quadro = requestAnimationFrame(animar);
  }

  function parar() {
    if (quadro !== null) cancelAnimationFrame(quadro);
    quadro = null;
  }

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) parar();
    else iniciar();
  });
  window.addEventListener("resize", ajustar);

  ajustar();
  iniciar();
})();
