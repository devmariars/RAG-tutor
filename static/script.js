console.log("JavaScript do RAG Tutor conectado! 🚀");
// =========================================================
// 1. ELEMENTOS PRINCIPAIS
// =========================================================
const formulario = document.querySelector("#form-pergunta");
const campoPergunta = document.querySelector("#pergunta");
const botaoEnviar = formulario.querySelector('button[type="submit"]');
const areaResposta = document.querySelector(".area-resposta");
const historicoChat = document.querySelector("#historico-chat");
// =========================================================
// 2. CHAT FLUTUANTE
// =========================================================
const botaoChat = document.querySelector("#botao-chat");
const painelChat = document.querySelector("#area-chat");
const fecharChat = document.querySelector("#fechar-chat");
const overlayChat = document.querySelector("#overlay-chat");
// =========================================================
// 3. MENU
// =========================================================
const linkPerguntar =
    document.querySelector('.menu-topo a[href="#area-chat"]');
// =========================================================
// 4. FORMATAÇÃO DA RESPOSTA
// =========================================================
function formatarResposta(texto) {
    if (!texto) {
        return "";
    }
    return texto
        .replace(/\*\*(.*?)\*\*/g, "$1")
        .replace(/\*(.*?)\*/g, "$1")
        .replace(/^#{1,6}\s+/gm, "")
        .trim();
}
// =========================================================
// 5. ABRIR / FECHAR CHAT
// =========================================================
function abrirChat() {
    document.body.classList.add("chat-aberto");
    painelChat.classList.add("aberto");
    painelChat.setAttribute(
        "aria-hidden",
        "false"
    );
    botaoChat.setAttribute(
        "aria-expanded",
        "true"
    );
    setTimeout(function () {
        campoPergunta.focus();
    }, 200);
}
function fecharPainelChat() {
    document.body.classList.remove("chat-aberto");
    painelChat.classList.remove("aberto");
    painelChat.setAttribute(
        "aria-hidden",
        "true"
    );
    botaoChat.setAttribute(
        "aria-expanded",
        "false"
    );
}
botaoChat.addEventListener(
    "click",
    abrirChat
);
fecharChat.addEventListener(
    "click",
    fecharPainelChat
);
overlayChat.addEventListener(
    "click",
    fecharPainelChat
);
// ESC fecha o chat
document.addEventListener(
    "keydown",
    function (evento) {
        if (
            evento.key === "Escape" &&
            document.body.classList.contains("chat-aberto")
        ) {
            fecharPainelChat();
        }
    }
);
// =========================================================
// 6. CRIA MENSAGEM
// =========================================================
function criarMensagem(
    tipo,
    texto,
    fontes = []
) {
    const mensagem =
        document.createElement("div");
    mensagem.classList.add(
        "mensagem-chat",
        tipo === "usuario"
            ? "mensagem-usuario"
            : "mensagem-rag"
    );
    const autor =
        document.createElement("span");
    autor.classList.add(
        "autor-mensagem"
    );
    autor.textContent =
        tipo === "usuario"
            ? "Você"
            : "RAG Tutor";
    const conteudo =
        document.createElement("p");
    conteudo.classList.add(
        "conteudo-mensagem"
    );
    conteudo.textContent = texto;
    mensagem.appendChild(autor);
    mensagem.appendChild(conteudo);
    // =====================================================
    // FONTES
    // =====================================================
    if (
        tipo === "rag" &&
        fontes.length > 0
    ) {
        const blocoFontes =
            document.createElement("div");
        blocoFontes.classList.add(
            "fontes-mensagem"
        );
        blocoFontes.textContent =
            `Fonte: ${fontes.join(", ")}`;
        mensagem.appendChild(
            blocoFontes
        );
    }
    historicoChat.appendChild(
        mensagem
    );
    // Rola somente dentro do chat
    requestAnimationFrame(function () {
        areaResposta.scrollTo({
            top: areaResposta.scrollHeight,
            behavior: "smooth"
        });
    });
    return mensagem;
}
// =========================================================
// 7. ENVIO DA PERGUNTA
// =========================================================
let consultaEmAndamento = false;
formulario.addEventListener(
    "submit",
    async function (evento) {
        evento.preventDefault();
        const pergunta =
            campoPergunta.value.trim();
        if (
            !pergunta ||
            consultaEmAndamento
        ) {
            return;
        }
        consultaEmAndamento = true;
        // Pergunta do usuário
        criarMensagem(
            "usuario",
            pergunta
        );
        campoPergunta.value = "";
        campoPergunta.disabled = true;
        botaoEnviar.disabled = true;
        // Loading
        const mensagemLoading =
            criarMensagem(
                "rag",
                "Consultando a base..."
            );
        try {
            const resposta =
                await fetch(
                    "/perguntar",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type":
                                "application/json"
                        },
                        body: JSON.stringify({
                            pergunta: pergunta
                        })
                    }
                );
            if (!resposta.ok) {
                throw new Error(
                    `Erro HTTP: ${resposta.status}`
                );
            }
            const dados =
                await resposta.json();
            console.log(
                "Resposta do RAG:",
                dados
            );
            mensagemLoading.remove();
            criarMensagem(
                "rag",
                formatarResposta(
                    dados.resposta
                ),
                dados.fontes || []
            );
        } catch (erro) {
            console.error(
                "Erro ao consultar o RAG:",
                erro
            );
            mensagemLoading.remove();
            criarMensagem(
                "rag",
                "Não foi possível consultar o RAG Tutor neste momento."
            );
        } finally {
            consultaEmAndamento = false;
            campoPergunta.disabled = false;
            botaoEnviar.disabled = false;
            campoPergunta.focus();
        }
    }
);
// =========================================================
// 8. DESTAQUE AMARELO
// =========================================================
function destacar(elementos) {
    elementos.forEach(function (elemento) {
        if (elemento) {
            elemento.classList.add(
                "destaque-menu"
            );
        }
    });
    setTimeout(function () {
        elementos.forEach(function (elemento) {
            if (elemento) {
                elemento.classList.remove(
                    "destaque-menu"
                );
            }
        });
    }, 1500);
}
// =========================================================
// 9. ÓRBITA DOS PLANETAS
// =========================================================
const sistemaOrbital =
    document.querySelector(".sistema-orbital");
const planetas =
    document.querySelectorAll(".sistema-orbital .planeta");
let anguloOrbita = 0;
let ultimoTempoOrbita = null;
let orbitaPausada = false;
planetas.forEach(function (planeta) {
    planeta.addEventListener("mouseenter", function () {
        orbitaPausada = true;
    });
    planeta.addEventListener("mouseleave", function () {
        orbitaPausada = false;
        ultimoTempoOrbita = performance.now();
    });
});
planetas.forEach(function (planeta) {
    planeta.addEventListener("mouseenter", function () {
        orbitaPausada = true;
    });
    planeta.addEventListener("mouseleave", function () {
        orbitaPausada = false;
        ultimoTempoOrbita = performance.now();
    });
});
// 30 segundos para uma volta completa
const duracaoVolta = 50000;
function animarOrbita(tempoAtual) {
    if (!sistemaOrbital || planetas.length === 0) {
        return;
    }
    if (ultimoTempoOrbita === null) {
        ultimoTempoOrbita = tempoAtual;
    }
    const delta =
        tempoAtual - ultimoTempoOrbita;
    ultimoTempoOrbita = tempoAtual;
   // Avança o ângulo somente quando a órbita não estiver pausada
if (!orbitaPausada) {
    anguloOrbita +=
        (delta / duracaoVolta) *
        Math.PI *
        2;
}
    const largura =
        sistemaOrbital.clientWidth;
    const altura =
        sistemaOrbital.clientHeight;
    // Tamanho da elipse
    let raioX = largura * 0.38;
    let raioY = altura * 0.32;
    // Ajuste para telas menores
    if (window.innerWidth <= 768) {
        raioX = largura * 0.34;
        raioY = altura * 0.34;
    }
    planetas.forEach(function (planeta, indice) {
        // Distribui os 6 planetas igualmente
        const espacamento =
            (Math.PI * 2) / planetas.length;
        const angulo =
            anguloOrbita +
            indice * espacamento;
        const x =
            Math.cos(angulo) * raioX;
        const y =
            Math.sin(angulo) * raioY;
        // JS assume totalmente o posicionamento orbital
        planeta.style.left = "50%";
        planeta.style.top = "50%";
        planeta.style.right = "auto";
        planeta.style.bottom = "auto";
        planeta.style.transform =
            `translate(-50%, -50%) translate(${x}px, ${y}px)`;
        // Quem passa pela parte inferior da órbita
        // aparece visualmente mais à frente
        const profundidade =
            Math.sin(angulo);
        planeta.style.zIndex =
            profundidade > 0
                ? "5"
                : "2";
    });
    requestAnimationFrame(animarOrbita);
}
requestAnimationFrame(animarOrbita);
// =========================================================
// 10. CORREÇÃO AO VOLTAR PARA A ABA
// =========================================================
document.addEventListener(
    "visibilitychange",
    function () {
        if (!document.hidden) {
            ultimoTempoOrbita = performance.now();
        }
    }
);