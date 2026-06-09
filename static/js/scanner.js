const URL = "/static/model/";

let model, webcam, labelContainer, maxPredictions;
let lastPrediction = "";

async function init() {
    const modelURL = URL + "model.json";
    const metadataURL = URL + "metadata.json";

    model = await tmImage.load(modelURL, metadataURL);
    maxPredictions = model.getTotalClasses();

    const constraints = {
        facingMode: "environment"
    };

    webcam = new tmImage.Webcam(250, 250, false);
    await webcam.setup(constraints);
    await webcam.play();

    window.requestAnimationFrame(loop);

    document.getElementById("webcam-container").appendChild(webcam.canvas);

    labelContainer = document.getElementById("label-container");

    for (let i = 0; i < maxPredictions; i++) {
        labelContainer.appendChild(document.createElement("div"));
    }
}

async function loop() {
    webcam.update();
    await predict();
    window.requestAnimationFrame(loop);
}

async function predict() {
    const prediction = await model.predict(webcam.canvas);

    let bestPrediction = null;
    let highestProbability = 0;

    for (let i = 0; i < maxPredictions; i++) {
        const probability = prediction[i].probability;

        labelContainer.childNodes[i].innerHTML =
            prediction[i].className + ": " + probability.toFixed(2);

        if (probability > highestProbability) {
            highestProbability = probability;
            bestPrediction = prediction[i].className;
        }
    }

    if (highestProbability > 0.95) {
        if (bestPrediction !== lastPrediction) {
            lastPrediction = bestPrediction;
            getPokemonData(bestPrediction);
        }
    }
}

async function getPokemonData(name) {
    const response = await fetch("/get_pokemon", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: name
        })
    });

    const data = await response.json();

    if (data.success) {
        displayPokemon(data.pokemon);
    } else {
        document.getElementById("pokemon-card").innerHTML = `
            <div class="alert alert-warning mt-4 text-center">
                Pokémon not recognised.
            </div>
        `;
    }
}

function displayPokemon(pokemon) {
    document.getElementById("pokemon-card").innerHTML = `

        <div class="card shadow p-3 mt-4 mx-auto text-center" style="max-width: 420px;">

            <h3>Is this ${pokemon.name}?</h3>

            <img src="${pokemon.image}"
                 class="mx-auto my-3"
                 style="width: 220px; image-rendering: pixelated;">

            <p>${pokemon.description}</p>

            <div class="d-flex gap-2 justify-content-center mt-3">

                <button class="btn btn-success" onclick="addToCollection(${pokemon.id})">
                    Yes, add to collection
                </button>

                <button class="btn btn-danger" onclick="wrongScan()">
                    No, scanned wrong
                </button>

            </div>

            <p id="add-message" class="mt-3 fw-bold"></p>

        </div>
    `;
}   

async function addToCollection(pokemonId) {
    const response = await fetch("/add_to_collection", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            pokemon_id: pokemonId
        })
    });

    const data = await response.json();

    if (data.success) {
        document.getElementById("add-message").innerText =
            "Added to collection! Quantity: " + data.quantity;

        if (data.achievement_messages) {
            data.achievement_messages.forEach(message => {
                showAchievementPopup(message);
            });
        }
    }
}

function wrongScan() {
    document.getElementById("pokemon-card").innerHTML = `
        <div class="alert alert-danger mt-4 text-center">
            Scan cancelled. Try showing the card again.
        </div>
    `;

    lastPrediction = "";
}

function showAchievementPopup(message) {
    const popup = document.createElement("div");

    popup.className = "achievement-popup";

    popup.innerHTML = `
        <strong>Achievement Unlocked!</strong>
        <p>${message}</p>
    `;

    document.body.appendChild(popup);

    setTimeout(() => {
        popup.classList.add("show");
    }, 100);

    setTimeout(() => {
        popup.classList.remove("show");

        setTimeout(() => {
            popup.remove();
        }, 500);

    }, 4000);
}

