import streamlit as st
import nbformat
import zipfile
from io import BytesIO

def parse_notebook(notebook_content, include_markdown=False):
    """
    Parses the Jupyter Notebook and extracts sections based on `##` comments.
    """
    try:
        notebook = nbformat.reads(notebook_content, as_version=4)
    except Exception as e:
        st.error(f"Error reading the notebook: {e}")
        return None

    sections = []
    current_section = None

    for cell in notebook.cells:
        if cell.cell_type == 'code':
            lines = cell.source.split('\n')
            for line in lines:
                if line.strip().startswith('##'):
                    # New section found
                    if current_section:
                        sections.append(current_section)
                    current_section = {'title': line.strip(), 'content': []}
                elif current_section:
                    current_section['content'].append(line)
        elif cell.cell_type == 'markdown' and current_section and include_markdown:
            # Include Markdown content in the current section
            current_section['content'].append(f'"""\n{cell.source}\n"""')

    # Append the last section
    if current_section:
        sections.append(current_section)

    return sections

def create_zip(sections, use_title_as_filename=False):
    """
    Creates a zip file containing all the sections as .py files.
    """
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, section in enumerate(sections):
            if use_title_as_filename:
                # Use the section title as the filename (after cleaning)
                file_name = section['title'].strip('#').strip().replace(' ', '_').lower() + '.py'
            else:
                file_name = f"section_{i+1}.py"

            file_content = f"# {section['title']}\n" + '\n'.join(section['content'])
            zip_file.writestr(file_name, file_content)
    zip_buffer.seek(0)
    return zip_buffer

def main():
    """
    Main function for the Streamlit app.
    """
    st.title("Jupyter Notebook Parser 🚀")
    st.write("Upload your Jupyter Notebook (`.ipynb` file) and get separate `.py` files for each `##` section!")

    # Increase file upload limit to 500MB
   # st.set_option('server.maxUploadSize', 500)

    try:
        # Upload the notebook
        uploaded_file = st.file_uploader("Upload your Jupyter Notebook", type=["ipynb"])
        if uploaded_file is not None:
            notebook_content = uploaded_file.read()
            st.success("File uploaded successfully!")

            # Toggle for Markdown inclusion
            include_markdown = st.checkbox("Include Markdown cells in the output", value=False)

            # Toggle for custom file names
            use_title_as_filename = st.checkbox("Use section titles as file names", value=False)

            # Parse the notebook
            sections = parse_notebook(notebook_content, include_markdown)
            if sections is None:
                st.error("Failed to parse the notebook. Please check the file format.")
            elif not sections:
                st.warning("No sections found in the notebook. Make sure to use `##` for section headers.")
            else:
                st.success(f"Found {len(sections)} sections in the notebook!")

                # Create a zip file
                zip_buffer = create_zip(sections, use_title_as_filename)

                # Download button for the zip file
                st.download_button(
                    label="Download Sections as ZIP",
                    data=zip_buffer,
                    file_name="notebook_sections.zip",
                    mime="application/zip"
                )
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()