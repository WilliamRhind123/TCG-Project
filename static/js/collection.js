let shinyMode = false;

function getNormalImage(id) {
    return "/static/PokemonSpritesGen1/" + id + ".png";
}

function getShinyImage(id) {
    return "/static/PokemonSpritesGen1/Shiny/" + id + ".png";
}

function updateCardImages() {
    document.querySelectorAll(".pokemon-box").forEach(card => {
        const sprite = card.querySelector(".pokemon-sprite");
        const id = card.dataset.id;

        if (sprite) {
            sprite.src = shinyMode ? getShinyImage(id) : getNormalImage(id);
        }
    });

    const selectedCard = document.querySelector(".pokemon-box.selected");

    if (selectedCard) {
        updatePokemonDetails(selectedCard);
    }
}

function toggleShinyMode() {
    shinyMode = !shinyMode;

    updateCardImages();

    const button = document.getElementById("shiny-toggle-btn");

    if (button) {
        button.innerText = shinyMode ? "Normal Version" : "Shiny Version";
    }
}

function showPokemonDetails(card) {
    document.querySelectorAll(".pokemon-box").forEach(box => {
        box.classList.remove("selected");
    });

    card.classList.add("selected");

    updatePokemonDetails(card);
}

function updatePokemonDetails(card) {
    const detailImage = document.getElementById("detail-image");
    const isOwned = card.dataset.owned === "true";

    detailImage.src = shinyMode
        ? getShinyImage(card.dataset.id)
        : getNormalImage(card.dataset.id);

    if (isOwned) {
        detailImage.classList.remove("locked");
        detailImage.style.filter = "none";
        detailImage.style.opacity = "1";
    } else {
        detailImage.classList.add("locked");
        detailImage.style.filter = "grayscale(100%)";
        detailImage.style.opacity = "0.4";
    }

    document.getElementById("detail-name").innerText = card.dataset.name;
    document.getElementById("detail-type-image").src = card.dataset.typeImage;

    if (isOwned) {
        document.getElementById("detail-quantity").innerHTML =
            "<strong>Quantity:</strong> x" + card.dataset.quantity;
    } else {
        document.getElementById("detail-quantity").innerHTML =
            "<strong>Status:</strong> Not discovered yet";
    }

    document.getElementById("detail-type").innerHTML =
        "<strong>Type:</strong> " + card.dataset.type;

    document.getElementById("detail-species").innerHTML =
        "<strong>Species:</strong> " + card.dataset.species;

    document.getElementById("detail-height").innerHTML =
        "<strong>Height:</strong> " + card.dataset.height;

    document.getElementById("detail-weight").innerHTML =
        "<strong>Weight:</strong> " + card.dataset.weight;

    document.getElementById("detail-description").innerText =
        card.dataset.description;
}

function searchPokemon() {
    const input = document.getElementById("pokemon-search").value.toLowerCase();
    const cards = document.querySelectorAll(".pokemon-box");

    cards.forEach(card => {
        const name = card.dataset.name.toLowerCase();
        const type = card.dataset.type.toLowerCase();

        card.style.display =
            name.includes(input) || type.includes(input)
                ? "block"
                : "none";
    });
}

function sortPokemon(type) {
    const grid = document.querySelector(".pokemon-grid");
    const cards = Array.from(document.querySelectorAll(".pokemon-box"));

    if (type === "number") {
        cards.sort((a, b) => Number(a.dataset.id) - Number(b.dataset.id));
    }

    if (type === "az") {
        cards.sort((a, b) => a.dataset.name.localeCompare(b.dataset.name));
    }

    if (type === "owned") {
        cards.sort((a, b) => b.dataset.owned.localeCompare(a.dataset.owned));
    }

    if (type === "missing") {
        cards.sort((a, b) => a.dataset.owned.localeCompare(b.dataset.owned));
    }

    if (type === "quantity") {
        cards.sort((a, b) => Number(b.dataset.quantity) - Number(a.dataset.quantity));
    }

    cards.forEach(card => grid.appendChild(card));
}

function filterByType() {
    const selectedType = document.getElementById("type-sort").value;
    const cards = document.querySelectorAll(".pokemon-box");

    cards.forEach(card => {
        card.style.display =
            selectedType === "" || card.dataset.type.includes(selectedType)
                ? "block"
                : "none";
    });
}