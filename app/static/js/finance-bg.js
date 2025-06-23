// Animated finance-themed background for login/register pages
// Draws moving line graphs and floating shapes using Canvas

document.addEventListener('DOMContentLoaded', function() {
    const bg = document.createElement('canvas');
    bg.className = 'finance-bg-canvas';
    document.body.appendChild(bg);
    const ctx = bg.getContext('2d');

    function resize() {
        bg.width = window.innerWidth;
        bg.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Graph and shape data
    const graphs = [
        { color: 'rgba(62,214,194,0.18)', points: [], speed: 0.08, amp: 40, y: 0.25 },
        { color: 'rgba(30,233,182,0.13)', points: [], speed: 0.05, amp: 30, y: 0.55 },
        { color: 'rgba(62,166,255,0.10)', points: [], speed: 0.03, amp: 22, y: 0.75 }
    ];
    const shapes = Array.from({length: 7}, (_,i) => ({
        x: Math.random(),
        y: Math.random(),
        r: 18 + Math.random()*18,
        dx: (Math.random()-0.5)*0.018,
        dy: (Math.random()-0.5)*0.018,
        color: 'rgba(62,214,194,0.10)'
    }));

    function drawGraph(g, t) {
        const w = bg.width, h = bg.height;
        ctx.save();
        ctx.strokeStyle = g.color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        for (let i = 0; i <= 1; i += 0.02) {
            const x = i * w;
            const y = h * g.y + Math.sin(i*4 + t*g.speed) * g.amp + Math.cos(i*7 + t*g.speed*1.5) * g.amp*0.4;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
        ctx.restore();
    }

    function drawShape(s) {
        const w = bg.width, h = bg.height;
        ctx.save();
        ctx.beginPath();
        ctx.arc(s.x*w, s.y*h, s.r, 0, 2*Math.PI);
        ctx.fillStyle = s.color;
        ctx.fill();
        ctx.restore();
    }

    function animate() {
        ctx.clearRect(0,0,bg.width,bg.height);
        const t = Date.now()/1800;
        graphs.forEach(g => drawGraph(g, t));
        shapes.forEach(s => {
            drawShape(s);
            s.x += s.dx; s.y += s.dy;
            if (s.x < 0 || s.x > 1) s.dx *= -1;
            if (s.y < 0 || s.y > 1) s.dy *= -1;
        });
        requestAnimationFrame(animate);
    }
    animate();

    // Place canvas behind everything
    bg.style.position = 'fixed';
    bg.style.left = '0';
    bg.style.top = '0';
    bg.style.width = '100vw';
    bg.style.height = '100vh';
    bg.style.zIndex = '0';
    bg.style.pointerEvents = 'none';
});
