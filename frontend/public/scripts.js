document.addEventListener("DOMContentLoaded", function () {
    const clienteSelect = document.getElementById("cliente");
    const irParaSelecaoButton = document.getElementById("irParaSelecao");

    async function carregarClientes() {
        try {
            const response = await fetch("http://3.141.32.43:5000/api/salas");
            const salas = await response.json();

            const clientes = [...new Set(salas.map(sala => sala.cliente))];  // Extrai clientes únicos
            clientes.forEach(cliente => {
                const option = document.createElement("option");
                option.value = cliente;
                option.textContent = cliente;
                clienteSelect.appendChild(option);
            });
        } catch (error) {
            console.error("Erro ao carregar clientes:", error);
        }
    }

    clienteSelect.addEventListener("change", function () {
        irParaSelecaoButton.disabled = !this.value;
    });

    irParaSelecaoButton.addEventListener("click", function () {
        const cliente = clienteSelect.value;
        if (cliente) {
            window.location.href = `selecionar.html?cliente=${cliente}`;
        }
    });

    carregarClientes();
});

document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const cliente = urlParams.get("cliente");
    const quadrasContainer = document.getElementById("quadrasContainer");
    const diasContainer = document.getElementById("diasContainer");
    const horariosContainer = document.getElementById("horariosContainer");
    const videosContainer = document.getElementById("videosContainer");

    const clienteNome = document.getElementById("clienteNome");
    if (cliente && clienteNome) {
        clienteNome.textContent = `Cliente: ${cliente}`;
    }

    async function carregarQuadras() {
        try {
            const response = await fetch("http://3.141.32.43:5000/api/salas");
            const salas = await response.json();

            const quadras = [...new Set(salas.filter(sala => sala.cliente === cliente).map(sala => sala.quadra))];
            
            quadras.forEach(quadra => {
                const quadraButton = document.createElement("button");
                quadraButton.textContent = quadra;
                quadraButton.classList.add("quadra-button");
                quadraButton.addEventListener("click", function () {
                    carregarDias(quadra);
                });
                quadrasContainer.appendChild(quadraButton);
            });
        } catch (error) {
            console.error("Erro ao carregar quadras:", error);
        }
    }

    async function carregarDias(quadra) {
        try {
            const response = await fetch(`http://3.141.32.43:5000/api/dias/${quadra}`);
            const dias = await response.json();

            diasContainer.innerHTML = '';

            dias.forEach(dia => {
                const diaButton = document.createElement("button");
                diaButton.textContent = dia;
                diaButton.classList.add("dia-button");
                diaButton.addEventListener("click", function () {
                    carregarHorarios(quadra, dia);
                });
                diasContainer.appendChild(diaButton);
            });
        } catch (error) {
            console.error("Erro ao carregar dias:", error);
        }
    }

    async function carregarHorarios(quadra, dia) {
        try {
            const response = await fetch(`http://3.141.32.43:5000/api/horarios/${quadra}/${dia}`);
            const horarios = await response.json();

            horariosContainer.innerHTML = '';

            horarios.forEach(horario => {
                const horarioButton = document.createElement("button");
                horarioButton.textContent = horario;
                horarioButton.classList.add("horario-button");
                horarioButton.addEventListener("click", function () {
                    buscarVideos(quadra, dia, horario);
                });
                horariosContainer.appendChild(horarioButton);
            });
        } catch (error) {
            console.error("Erro ao carregar horários:", error);
        }
    }

    async function buscarVideos(quadra, dia, horario) {
        try {
            const response = await fetch(`http://3.141.32.43:5000/listavideos?cliente=${cliente}&quadra=${quadra}&dia=${dia}&horario=${horario}`);
            const videos = await response.json();

            videosContainer.innerHTML = "";

            if (videos.length === 0) {
                videosContainer.innerHTML = "<p>Nenhum vídeo encontrado.</p>";
                return;
            }

            videos.forEach(video => {
                const videoElement = document.createElement("div");
                videoElement.classList.add("video-item");
                videoElement.innerHTML = `
                    <h3>${video.nome}</h3>
                    <img src="${video.thumbnail}" alt="Thumbnail">
                    <a href="${video.url}" target="_blank">Assistir</a>
                `;
                videosContainer.appendChild(videoElement);
            });
        } catch (error) {
            console.error("Erro ao buscar vídeos:", error);
        }
    }

    carregarQuadras();
});
