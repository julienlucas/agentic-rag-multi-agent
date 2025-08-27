import gradio as gr
import hashlib
from typing import List, Dict
import os

from document_processor.file_handler import DocumentProcessor
from retriever.builder import RetrieverBuilder
from agents.workflow import AgentWorkflow
from config import constants, settings
from utils.logging import logger

# 1) Définir quelques exemples de données
#    (c'est-à-dire question + chemins vers les documents pertinents pour cette question).
EXAMPLES = {
    "Rapport Environnemental Google 2024": {
        "question": "Récupérez les valeurs d'efficacité PUE du centre de données dans l'installation 2 de Singapour en 2019 et 2022. Récupérez également la moyenne régionale CFE en Asie-Pacifique en 2023",
        "file_paths": ["examples/google-2024-environmental-report.pdf"]
    },
    "Rapport Technique DeepSeek-R1": {
        "question": "Résumez l'évaluation des performances du modèle DeepSeek-R1 sur toutes les tâches de codage par rapport au modèle OpenAI o1-mini",
        "file_paths": ["examples/DeepSeek Technical Report.pdf"]
    }
}

def main():
    processor = DocumentProcessor()
    retriever_builder = RetrieverBuilder()
    workflow = AgentWorkflow()

    # Define custom CSS for styling
    css = """
    .title {
        font-size: 1.5em !important;
        text-align: center !important;
        color: #FFD700;
    }

    .subtitle {
        font-size: 1em !important;
        text-align: center !important;
        color: #FFD700;
    }

    .text {
        text-align: center;
    }
    """

    js = """
    function createGradioAnimation() {
        var container = document.createElement('div');
        container.id = 'gradio-animation';
        container.style.fontSize = '2em';
        container.style.fontWeight = 'bold';
        container.style.textAlign = 'center';
        container.style.marginBottom = '20px';
        container.style.color = '#eba93f';

        var text = 'Bienvenue sur DocChat 🐥!';
        for (var i = 0; i < text.length; i++) {
            (function(i){
                setTimeout(function(){
                    var letter = document.createElement('span');
                    letter.style.opacity = '0';
                    letter.style.transition = 'opacity 0.1s';
                    letter.innerText = text[i];

                    container.appendChild(letter);

                    setTimeout(function() {
                        letter.style.opacity = '0.9';
                    }, 50);
                }, i * 250);
            })(i);
        }

        var gradioContainer = document.querySelector('.gradio-container');
        gradioContainer.insertBefore(container, gradioContainer.firstChild);

        return 'Animation created';
    }
    """

    with gr.Blocks(theme=gr.themes.Citrus(), title="DocChat 🐥", css=css, js=js) as demo:
        gr.Markdown("## DocChat: propulsé par Docling 🐥 et LangGraph", elem_classes="subtitle")
        gr.Markdown("# Comment ça marche ✨:", elem_classes="title")
        gr.Markdown("📤 Téléchargez vos document(s), entrez votre question puis cliquez sur Envoyer 📝", elem_classes="text")
        gr.Markdown("Ou vous pouvez sélectionner un des exemples dans le menu déroulant, cliquer sur Charger l'exemple puis Envoyer 📝", elem_classes="text")
        gr.Markdown("⚠️ **Note:** DocChat n'accepte que les documents aux formats: '.pdf', '.docx', '.txt', '.md'", elem_classes="text")

        # 2) Maintain the session state for retrieving doc changes
        session_state = gr.State({
            "file_hashes": frozenset(),
            "retriever": None
        })

        # 3) Layout
        with gr.Row():
            with gr.Column():
                # Section pour les Exemples
                gr.Markdown("### Exemple 📂")
                example_dropdown = gr.Dropdown(
                    label="Sélectionner un Exemple 🐥",
                    choices=list(EXAMPLES.keys()),
                    value=None,  # initialement non sélectionné
                )
                load_example_btn = gr.Button("Charger l'Exemple 🛠️")

                # Composants d'entrée standard
                files = gr.Files(label="📄 Télécharger les Documents", file_types=constants.ALLOWED_TYPES)
                question = gr.Textbox(label="❓ Question", lines=3)

                submit_btn = gr.Button("Envoyer 🚀")

            with gr.Column():
                answer_output = gr.Textbox(label="🐥 Réponse", interactive=False)
                verification_output = gr.Textbox(label="✅ Rapport de Vérification")

                # 4) Fonction d'aide pour charger l'exemple dans l'interface
        def load_example(example_key: str):
            """
            Étant donné une clé comme 'Exemple 1',
            lire les documents pertinents depuis le disque et retourner
            des objets de type fichier, plus la question d'exemple.
            """
            if not example_key or example_key not in EXAMPLES:
                return [], ""  # vide si non trouvé

            ex_data = EXAMPLES[example_key]
            question = ex_data["question"]
            file_paths = ex_data["file_paths"]

            # Préparer la liste de fichiers à retourner. On les lit depuis le disque pour
            # donner à Gradio quelque chose qu'il peut gérer comme des fichiers "téléchargés".
            loaded_files = []
            for path in file_paths:
                if os.path.exists(path):
                    # Gradio peut accepter un chemin directement, ou un objet de type fichier
                    loaded_files.append(path)
                else:
                    logger.warning(f"Fichier non trouvé: {path}")

            # La fonction peut retourner des listes correspondant aux sorties qu'on définit ci-dessous
            return loaded_files, question

        load_example_btn.click(
            fn=load_example,
            inputs=[example_dropdown],
            outputs=[files, question]
        )

        # 5) Flux standard pour la soumission de questions
        def process_question(question_text: str, uploaded_files: List, state: Dict):
            """Gérer les questions avec mise en cache des documents."""
            try:
                if not question_text.strip():
                    raise ValueError("❌ La question ne peut pas être vide")
                if not uploaded_files:
                    raise ValueError("❌ Aucun document téléchargé")

                current_hashes = _get_file_hashes(uploaded_files)

                if state["retriever"] is None or current_hashes != state["file_hashes"]:
                    logger.info("Traitement des documents nouveaux/modifiés...")
                    chunks = processor.process(uploaded_files)
                    retriever = retriever_builder.build_hybrid_retriever(chunks)

                    state.update({
                        "file_hashes": current_hashes,
                        "retriever": retriever
                    })

                result = workflow.full_pipeline(
                    question=question_text,
                    retriever=state["retriever"]
                )

                return result["draft_answer"], result["verification_report"], state

            except Exception as e:
                logger.error(f"Erreur de traitement: {str(e)}")
                return f"❌ Erreur: {str(e)}", "", state

        submit_btn.click(
            fn=process_question,
            inputs=[question, files, session_state],
            outputs=[answer_output, verification_output, session_state]
        )

    demo.launch(server_name="127.0.0.1", server_port=5000, share=True)

def _get_file_hashes(uploaded_files: List) -> frozenset:
    """Générer des hashes SHA-256 pour les fichiers téléchargés."""
    hashes = set()
    for file in uploaded_files:
        with open(file.name, "rb") as f:
            hashes.add(hashlib.sha256(f.read()).hexdigest())
    return frozenset(hashes)

if __name__ == "__main__":
    main()
