const aa = require ('./aa.json')

const getName = (sk) => {
    if (sk.layers) {
        for (let v of sk.layers) {
            getName(v);
        }
    }
    console.log(sk.name);
}

getName (aa)

