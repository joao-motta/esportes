document.addEventListener("DOMContentLoaded", function () {
    // Verifique se o Amplify foi carregado antes de configurar
    if (typeof Amplify === "undefined") {
        console.error("Amplify não foi carregado corretamente");
        return; // Saia da função se Amplify não estiver definido
    }

    // Configurar o Amplify
    fetch('https://main.d1636gox262hyh.amplifyapp.com/aws-exports.js')
        .then(response => response.text())  // Lê o arquivo como texto
        .then(data => {
            // Use eval para executar o código JavaScript
            const awsconfig = eval(data); // Transformar a string em código JavaScript e obter o objeto
            Amplify.configure(awsconfig); // Configurar o Amplify com a configuração carregada
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
