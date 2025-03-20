document.addEventListener("DOMContentLoaded", function () {
    // Página 1 - Selecione Cliente (index.html)
    if (document.getElementById("cliente")) {
        const clienteSelect = document.getElementById("cliente");
        const irParaSalaButton = document.getElementById("irParaSala");

        async function carregarClientes() {
            // Aqui você irá buscar a lista de clientes da sua API
            const response = await fetch("http://3.141.32.43:5000/api/clientes");
            const clientes = await response.json();
            
            clientes.forEach(cliente => {
                const option = document.createElement("option");
                option.value = cliente.id;
                option.textContent = cliente.nome;
                clienteSelect.appendChild(option);
            });
        }

        clienteSelect.addEventListener("change", function () {
            irParaSalaButton.disabled = !this.value;
        });

        irParaSalaButton.addEventListener("click", function () {
            const clienteId = clienteSelect.value;
            if (clienteId) {
                window.location.href = `sala.html?cliente=${clienteId}`;
            }
        });

        carregarClientes();
    }

    // Página 2 - Selecione Sala (sala.html)
    if (document.getElementById("sala")) {
        const urlParams = new URLSearchParams(window.location.search);
        const clienteId = urlParams.get("cliente");
        const salaSelect = document.getElementById("sala");
        const irParaSelecaoButton = document.getElementById("irParaSelecao");
        const clienteNome = document.getElementById("clienteNome");

        async function carregarSalas() {
            // Aqui você irá buscar a lista de salas da sua API
            const response = await fetch(`http://3.141.32.43:5000/api/salas?clienteId=${clienteId}`);
            const salas = await response.json();
            
            salas.forEach(sala => {
                const option = document.createElement("option");
                option.value = sala.id;
                option.textContent = sala.nome;
                salaSelect.appendChild(option);
            });
        }

        // Carregar o nome do cliente
        if (clienteId && clienteNome) {
            fetch(`http://3.141.32.43:5000/api/clientes/${clienteId}`)
                .then(response => response.json())
                .then(cliente => {
                    clienteNome.textContent = cliente ? `Cliente: ${cliente.nome}` : 'Cliente não encontrado';
                })
                .catch(error => console.error("Erro ao buscar nome do cliente:", error));
        }

        salaSelect.addEventListener("change", function () {
            irParaSelecaoButton.disabled = !this.value;
        });

        irParaSelecaoButton.addEventListener("click", function () {
            const salaId = salaSelect.value;
            if (salaId) {
                window.location.href = `selecionar.html?cliente=${clienteId}&sala=${salaId}`;
            }
        });

        carregarSalas();
    }

    // Página 3 - Selecione Dia, Horário e Vídeos (selecionar.html)
    if (document.getElementById("diasContainer")) {
        const urlParams = new URLSearchParams(window.location.search);
        const clienteId = urlParams.get("cliente");
        const salaId = urlParams.get("sala");
        const diasContainer = document.getElementById("diasContainer");
        const horariosContainer = document.getElementById("horariosContainer");
        const videosContainer = document.getElementById("videosContainer");

        // Carregar Cliente e Sala
        fetch(`http://3.141.32.43:5000/api/clientes/${clienteId}`)
            .then(response => response.json())
            .then(cliente => {
                document.getElementById("clienteNome").textContent = `Cliente: ${cliente.nome}`;
            });

        fetch(`http://3.141.32.43:5000/api/salas/${salaId}`)
            .then(response => response.json())
            .then(sala => {
                document.getElementById("salaNome").textContent = `Sala: ${sala.nome}`;
            });

        // Carregar Dias
        async function carregarDias() {
            const response = await fetch(`http://3.141.32.43:5000/api/dias/${salaId}`);
            const dias = await response.json();

            dias.forEach(dia => {
                const diaButton = document.createElement("button");
                diaButton.textContent = dia;
                diaButton.classList.add("dia-button");
                diaButton.addEventListener("click", function () {
                    carregarHorarios(dia);
                });
                diasContainer.appendChild(diaButton);
            });
        }

        // Carregar Horários
        async function carregarHorarios(dia) {
            const response = await fetch(`http://3.141.32.43:5000/api/horarios/${salaId}/${dia}`);
            const horarios = await response.json();

            horariosContainer.innerHTML = '';
            horarios.forEach(horario => {
                const horarioButton = document.createElement("button");
                horarioButton.textContent = horario;
                horarioButton.classList.add("horario-button");
                horarioButton.addEventListener("click", function () {
                    buscarVideos(dia, horario);
                });
                horariosContainer.appendChild(horarioButton);
            });
        }

        // Buscar Vídeos
        async function buscarVideos(dia, horario) {
            const response = await fetch(`http://3.141.32.43:5000/listavideos?cameraIP=${salaId}&dia=${dia}&horario=${horario}`);
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
        }

        carregarDias();
    }
});
