document.addEventListener("DOMContentLoaded", function () {
    const apiBaseUrl = "http://3.141.32.43:5000/api";

    // Função genérica para carregar opções de dropdown
    async function carregarOptions(apiUrl, elementId, placeholder = "Selecione uma opção") {
        const response = await fetch(apiUrl);
        const data = await response.json();
        const selectElement = document.getElementById(elementId);
        selectElement.innerHTML = `<option value="">${placeholder}</option>`;
        data.forEach(item => {
            const option = document.createElement("option");
            option.value = item.id;
            option.textContent = item.nome || item.dia || item.horario; // Ajustar conforme a API
            selectElement.appendChild(option);
        });
    }

    // Página 1 - Selecione Cliente
    if (document.getElementById("cliente")) {
        const clienteSelect = document.getElementById("cliente");
        const irParaSalaButton = document.getElementById("irParaSala");
        const loadingMessage = document.getElementById("loadingMessage"); // Carregamento

        async function carregarClientes() {
            loadingMessage.style.display = 'block'; // Exibe a mensagem de carregamento
            const response = await fetch(`${apiBaseUrl}/clientes`);
            const clientes = await response.json();
            loadingMessage.style.display = 'none'; // Oculta a mensagem de carregamento
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

    // Página 2 - Selecione Sala
    if (document.getElementById("sala")) {
        const urlParams = new URLSearchParams(window.location.search);
        const clienteId = urlParams.get("cliente");
        const salaSelect = document.getElementById("sala");
        const irParaSelecaoButton = document.getElementById("irParaSelecao");

        async function carregarSalas() {
            const response = await fetch(`${apiBaseUrl}/salas/${clienteId}`);
            const salas = await response.json();
            salas.forEach(sala => {
                const option = document.createElement("option");
                option.value = sala.id;
                option.textContent = sala.nome;
                salaSelect.appendChild(option);
            });
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

    // Página 3 - Selecione Dia, Horário e Vídeos
    if (document.getElementById("diasContainer")) {
        const urlParams = new URLSearchParams(window.location.search);
        const clienteId = urlParams.get("cliente");
        const salaId = urlParams.get("sala");
        const diasContainer = document.getElementById("diasContainer");
        const horariosContainer = document.getElementById("horariosContainer");
        const videosContainer = document.getElementById("videosContainer");
        const buscarVideosButton = document.getElementById("buscarVideos");

        async function carregarDias(clienteId, salaId) {
            try {
                console.log("Carregando dias...");
                const response = await fetch(`${apiBaseUrl}/dias/${clienteId}/${salaId}`);
                const dias = await response.json();
                console.log("Resposta recebida para dias:", dias);
                if (!dias || dias.length === 0) {
                    console.log("Nenhum dia encontrado");
                    return;
                }
                dias.forEach(dia => {
                    const diaButton = document.createElement("button");
                    diaButton.textContent = dia.dia; // Verifique se o campo "dia" está correto
                    diaButton.dataset.id = dia.id;
                    diaButton.classList.add("dia-button");
                    diaButton.addEventListener("click", function () {
                        carregarHorarios(clienteId, salaId, dia.id); // Passando os parâmetros corretos
                    });
                    diasContainer.appendChild(diaButton);
                });
            } catch (error) {
                console.error("Erro ao carregar os dias:", error);
            }
        }

        async function carregarHorarios(clienteId, salaId, diaId) {
            try {
                console.log(`Carregando horários para o dia ${diaId}...`);
                const response = await fetch(`${apiBaseUrl}/horarios/${clienteId}/${salaId}/${diaId}`);
                const horarios = await response.json();
                console.log("Resposta recebida para horários:", horarios);
                if (!horarios || horarios.length === 0) {
                    console.log("Nenhum horário encontrado");
                    return;
                }
                horariosContainer.innerHTML = ''; // Limpa a lista de horários
                horarios.forEach(horario => {
                    const horarioButton = document.createElement("button");
                    horarioButton.textContent = horario.horario; // Verifique se o campo "horario" está correto
                    horarioButton.dataset.id = horario.id;
                    horarioButton.classList.add("horario-button");
    
                    horarioButton.addEventListener("click", function () {
                        const selectedButton = document.querySelector(".horario-button.selected");
                        if (selectedButton) {
                            selectedButton.classList.remove("selected");
                        }
                        horarioButton.classList.add("selected");
    
                        buscarVideos(clienteId, salaId, diaId, horario.id); // Passando os parâmetros corretos
                    });
    
                    horariosContainer.appendChild(horarioButton);
                });
            } catch (error) {
                console.error("Erro ao carregar os horários:", error);
            }
        }

        async function buscarVideos(clienteId, salaId, diaId, horarioId) {
            const response = await fetch(`${apiBaseUrl}/videos/${clienteId}/${salaId}/${diaId}/${horarioId}`);
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
                    <h3>Vídeo</h3>
                    <a href="${video.video_url}" target="_blank">
                        <img src="thumbnail_placeholder.jpg" alt="Thumbnail" />
                        Assistir
                    </a>
                `;
                videosContainer.appendChild(videoElement);
            });
        }

        buscarVideosButton.addEventListener("click", function () {
            const selectedDay = document.querySelector(".dia-button.selected");
            const selectedTime = document.querySelector(".horario-button.selected");
            if (!selectedDay || !selectedTime) {
                alert("Por favor, selecione um dia e horário.");
                return;
            }
            buscarVideos(clienteId, salaId, selectedDay.dataset.id, selectedTime.dataset.id);
        });

        carregarDias(clienteId, salaId); // Chama a função assim que a página carregar
    }
});
