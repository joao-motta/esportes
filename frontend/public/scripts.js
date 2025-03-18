// Importando o Amplify como um módulo ES6
import { Amplify } from 'https://cdn.jsdelivr.net/npm/aws-amplify@latest/dist/aws-amplify.min.js';

document.addEventListener("DOMContentLoaded", function () {
    // Agora o Amplify é carregado corretamente
    fetch('https://main.d1636gox262hyh.amplifyapp.com/aws-exports.js')
        .then(response => response.text())
        .then(data => {
            // Aqui o arquivo aws-exports.js é processado corretamente
            const script = document.createElement('script');
            script.type = 'module';
            script.textContent = `
                import awsconfig from 'data:text/javascript;base64,${btoa(data)}';
                Amplify.configure(awsconfig);
            `;
            document.head.appendChild(script);
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
