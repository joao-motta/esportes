document.addEventListener("DOMContentLoaded", function () {
    // Carregar o arquivo aws-exports.js como JSON
    fetch('https://main.d1636gox262hyh.amplifyapp.com/aws-exports.js')
        .then(response => response.text())  // Pega o conteúdo do arquivo como texto
        .then(data => {
            try {
                // Se o conteúdo for um JSON válido, use JSON.parse
                const awsconfig = JSON.parse(data);
                Amplify.configure(awsconfig);  // Configura o Amplify com as configurações do awsconfig
            } catch (error) {
                console.error("Erro ao processar aws-exports.js:", error);
            }
        })
        .catch(error => {
            console.error("Erro ao carregar aws-exports.js:", error);
        });

    // Função para carregar as salas
    const salaSelect = document.getElementById("sala");
    const irParaSelecaoButton = document.getElementById("irParaSelecao");

    async function carregarSalas() {
        try {
            const response = await fetch("http://18.219.146.25:5000/api/salas");
            const salas = await response.json();

            salas.forEach(sala => {
                const option = document.createElement("option");
                option.value = sala.id;
                option.textContent = sala.nome;
                salaSelect.appendChild(option);
            });
        } catch (error) {
            console.error("Erro ao carregar salas:", error);
        }
    }

    salaSelect.addEventListener("change", function () {
        irParaSelecaoButton.disabled = !this.value;
    });

    irParaSelecaoButton.addEventListener("click", function () {
        const salaId = salaSelect.value;
        if (salaId) {
            window.location.href = `selecionar.html?sala=${salaId}`;
        }
    });

    carregarSalas();
});
