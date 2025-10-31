import agreement_comparision
import dataExtraction
import json
import streamlit as st
import schedule
import threading
import time
import scraping,notification


def run_scheduler():
    schedule.every().day.at("00:00").do(scraping.call_scrape_function)
    # schedule.every(1).minute.do(scraping.call_scrape_function)
    while True:
        schedule.run_pending()
        time.sleep(5)  


# Start scheduler in background thread so Streamlit doesn’t block
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    # Mapping of agreement type to respective JSON file
    try:
        AGREEMENT_JSON_MAP = {
            "Data Processing Agreement": "jsonFiles/dpa.json",
            "Joint Controller Agreement": "jsonFiles/jca.json",
            "Controller-to-Controller Agreement": "jsonFiles/c2c.json",
            "Processor-to-Subprocessor Agreement": "jsonFiles/subprocessing.json",
            "Standard Contractual Clauses": "jsonFiles/scc.json",
            
        }

        st.markdown("""
            <style>
            /* Target the upload drop area text */
            [data-testid="stFileUploaderDropzone"] div div::before {
                content: "📁 Drag and drop your PDF here (Max 2 MB)";
                display: block;
                font-size: 14px;
                color: White;
                font-weight: 500;
                text-align: center;
                margin-bottom: 0.5rem;
            }


            /* Hide Streamlit's default text */
            [data-testid="stFileUploaderDropzone"] div div span {
                display: none;
            }
            </style>
        """, unsafe_allow_html=True)

        st.title("📄 Contract Compliance Checker")


        # File upload
        uploaded_file = st.file_uploader("Upload an agreement (PDF only)", type=["pdf"])


        if uploaded_file is not None:
            file_size_mb = uploaded_file.size / (1024 * 1024)  # Convert bytes to megabytes
            
            if file_size_mb > 2:
                st.error("File size exceeds 2 MB. Please upload a smaller file.")
            else:
                with open("temp_uploaded.pdf", "wb") as f:
                    f.write(uploaded_file.read())


                st.info("Processing your file...")


                # Step 1: Identify the type of agreement
                agreement_type = agreement_comparision.document_type("temp_uploaded.pdf")
                st.write("**Detected Document Type:**", agreement_type)


                if agreement_type in AGREEMENT_JSON_MAP:
                    # Step 2: Extract clauses
                    unseen_data = dataExtraction.Clause_extraction("temp_uploaded.pdf")


                    st.success("Clause Extraction Completed!!!")
                    # Step 3: Load the respective template JSON
                    template_file = AGREEMENT_JSON_MAP[agreement_type]
                    with open(template_file, "r", encoding="utf-8") as f:
                        template_data = json.load(f)


                    # Step 4: Compare agreements
                    result = agreement_comparision.compare_agreements(unseen_data, template_data)


                    # Show results
                    st.subheader("📊 Comparison Result")
                    st.write(result)
                    body = f"""Dear [Recipient's Name],

                            Thank you for submitting the {agreement_type} for review. 
                            We've completed a detailed comparison against the GDPR-compliant template and identified several areas 
                            where the current contract deviates from best practices and regulatory expectations.
                            
                            
                        \n Comparison Result: {result}"""
                    notification.send_notification("Comparison Result", body)

                else:
                    st.error(f"No template found for detected type: {agreement_type}")
    except Exception as e:
        print("Error Occured in document comparision", e)
        notification.send_notification("Error Occured in document comparision", f"Error is {e}")
        # notification.slack_notification(f"Error Occured in document comparision, Error is {e}")