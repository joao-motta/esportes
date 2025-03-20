document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const clienteNome = urlParams.get("cliente");
    const salaNome = urlParams.get("sala");

    // Página 1 - Selecione Cliente (index.html)
    if (document.getElementById("cliente")) {
        const clienteSelect = document.getElementById("cliente");
        const irParaSalaButton = document.getElementById("irParaSala");

        async function carregarClientes() {
            const response = await fetch("http://3.141.32.43:5000/api/clientes");
            const clientes = await response.json();
            
            clientes.forEach(cliente => {
                const option = document.createElement("option");
                option.value = cliente.nome;
                option.textContent = cliente.nome;
                clienteSelect.appendChild(option);
            });
        }

        clienteSelect.addEventListener("change", function () {
            irParaSalaButton.disabled = !this.value;
        });

        irParaSalaButton.addEventListener("click", function () {
            if (clienteSelect.value) {
                window.location.href = `sala.html?cliente=${encodeURIComponent(clienteSelect.value)}`;
            }
        });

        carregarClientes();
    }

    // Página 2 - Selecione Sala (sala.html)
    if (document.getElementById("sala")) {
        if (!clienteNome) {
            alert("Erro: Cliente não selecionado.");
            window.location.href = "index.html";
            return;
        }

        document.getElementById("clienteNome").textContent = `Cliente: ${clienteNome}`;
        const salaSelect = document.getElementById("sala");
        const irParaSelecaoButton = document.getElementById("irParaSelecao");

        async function carregarSalas() {
            const response = await fetch(`http://3.141.32.43:5000/api/salas?cliente=${encodeURIComponent(clienteNome)}`);
            const salas = await response.json();
            
            salas.forEach(sala => {
                const option = document.createElement("option");
                option.value = sala.nome;
                option.textContent = sala.nome;
                salaSelect.appendChild(option);
            });
        }

        salaSelect.addEventListener("change", function () {
            irParaSelecaoButton.disabled = !this.value;
        });

        irParaSelecaoButton.addEventListener("click", function () {
            if (salaSelect.value) {
                window.location.href = `selecionar.html?cliente=${encodeURIComponent(clienteNome)}&sala=${encodeURIComponent(salaSelect.value)}`;
            }
        });

        carregarSalas();
    }

    // Página 3 - Selecione Dia, Horário e Vídeos (selecionar.html)
    if (document.getElementById("diasContainer")) {
        if (!clienteNome || !salaNome) {
            alert("Erro: Cliente ou Sala não selecionados corretamente.");
            window.location.href = "index.html";
            return;
        }

        document.getElementById("clienteNome").textContent = `Cliente: ${clienteNome}`;
        document.getElementById("salaNome").textContent = `Sala: ${salaNome}`;

        async function carregarDias() {
            const response = await fetch(`http://3.141.32.43:5000/api/dias?sala=${encodeURIComponent(salaNome)}`);
            const dias = await response.json();
            const diasContainer = document.getElementById("diasContainer");

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

        async function carregarHorarios(dia) {
            const response = await fetch(`http://3.141.32.43:5000/api/horarios?sala=${encodeURIComponent(salaNome)}&dia=${dia}`);
            const horarios = await response.json();
            const horariosContainer = document.getElementById("horariosContainer");
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

        async function buscarVideos(dia, horario) {
            const response = await fetch(`http://3.141.32.43:5000/listavideos?sala=${encodeURIComponent(salaNome)}&dia=${dia}&horario=${horario}`);
            const videos = await response.json();
            const videosContainer = document.getElementById("videosContainer");
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