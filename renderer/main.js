document.addEventListener("DOMContentLoaded", () => {
    let renderer = PIXI.autoDetectRenderer(1000,1000);

    document.body.appendChild(renderer.view);

    let stage = new PIXI.Container();


    var c = io.connect("http://localhost:5000")
    console.log(c.connected)
    c.on("data", function(data) {
        var circle = new PIXI.Graphics();
        data.samples.forEach((e) => {
            var pos = polarToCart(e.distance, e.angle / 1000)
            console.log(e)
        circle.beginFill(0xffffff)
        circle.drawCircle(pos.x + 500,pos.y + 500, 1)
        circle.endFill()
        stage.addChild(circle)
        })
        renderer.render(stage)
    })
    c.emit("start")

});

function polarToCart(distance, theta) {
         return {"x": distance*Math.cos(theta), "y": distance*Math.sin(theta)}
}
