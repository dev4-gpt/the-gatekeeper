import pandas as pd
import streamlit as st
from dotenv import load_dotenv
load_dotenv()  # pull GOOGLE_API_KEY (and others) from .env into os.environ
from gatekeeper.engine import compute_lead_score, run as engine_run
from gatekeeper import messages
from gatekeeper.storage import get_lead, init_db, list_leads, save_lead


def main() -> None:
    st.set_page_config(page_title="Gatekeeper – Lead Qualification", layout="wide")
    init_db()

    st.title("Gatekeeper – Lead Qualification Dashboard")

    st.sidebar.header("Qualify a new lead")

    need_text = st.sidebar.text_area(
        "Need",
        placeholder="What's driving you to look at something like this right now?",
    )
    authority_text = st.sidebar.text_input(
        "Authority",
        placeholder="Who signs off on a partnership like this?",
    )
    budget_text = st.sidebar.text_input(
        "Budget",
        placeholder="Do you have budget allocated or need approval?",
    )
    timeline_text = st.sidebar.text_input(
        "Timeline",
        placeholder="This quarter, next quarter, or exploring?",
    )

    if st.sidebar.button("Run qualification"):
        answers = {
            "need": need_text,
            "authority": authority_text,
            "budget": budget_text,
            "timeline": timeline_text,
        }
        result = engine_run(answers)
        scores = result.get("scores", {})
        lead_score, confidence_band = compute_lead_score(scores)

        lead_id = save_lead(
            answers=answers,
            scores=scores,
            outcome=result.get("outcome") or "",
            reason=result.get("reason") or "",
            lead_score=lead_score,
            confidence_band=confidence_band,
        )

        st.sidebar.success(
            f"Lead saved with ID {lead_id} (score {lead_score}, {confidence_band} confidence)."
        )

    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("Leads")
        leads = list_leads()
        if leads:
            df = pd.DataFrame(leads)
            display_cols = [
                "id",
                "created_at",
                "outcome",
                "lead_score",
                "confidence_band",
                "need_score",
                "authority_score",
                "budget_score",
                "timeline_score",
            ]
            st.dataframe(df[display_cols])

            selected_id = st.number_input(
                "View lead by ID",
                min_value=int(df["id"].min()),
                max_value=int(df["id"].max()),
                value=int(df["id"].iloc[0]),
                step=1,
            )
        else:
            st.info("No leads yet. Add one using the form on the left.")
            selected_id = None

    with col2:
        st.subheader("Lead detail")
        if selected_id is not None:
            lead = get_lead(int(selected_id))
            if lead is None:
                st.warning("Lead not found.")
            else:
                answers = {
                    "need": lead["need_text"],
                    "authority": lead["authority_text"],
                    "budget": lead["budget_text"],
                    "timeline": lead["timeline_text"],
                }
                scores = {
                    "need": lead["need_score"],
                    "authority": lead["authority_score"],
                    "budget": lead["budget_score"],
                    "timeline": lead["timeline_score"],
                }

                recap = messages.build_recap(answers, scores)
                st.markdown("### Recap")
                st.code(recap, language="text")

                st.markdown("### Outcome")
                st.write(f"**Status:** {lead['outcome']}")
                st.write(
                    f"**Lead score:** {lead['lead_score']} ({lead['confidence_band']} confidence)"
                )
                st.write(f"**Reason code:** `{lead['reason']}`")
                st.markdown("### Next step")
                st.write(messages.describe_outcome(lead["outcome"], lead["reason"]))

                st.markdown("### Raw answers")
                for key in ("need_text", "authority_text", "budget_text", "timeline_text"):
                    label = key.replace("_text", "").capitalize()
                    st.write(f"**{label}:** {lead[key]}")
        else:
            st.write("Select a lead in the left column to view details.")


if __name__ == "__main__":
    main()

