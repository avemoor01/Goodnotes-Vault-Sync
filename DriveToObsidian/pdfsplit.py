import os
from pdf2image import pdf2image as pconvert
# from pdf2image import convert_from_path
import json

# Load configuration data from a JSON file ("config.json")
current_directory = os.getcwd()
input_folder = os.path.join(current_directory, "temp")
output_root = current_directory

dataFile = os.path.join(os.path.dirname(current_directory), "data.json")

with open(dataFile, 'r') as file:
    data = json.load(file)

for _ in range(4):
    output_root = os.path.dirname(output_root)
output_root = os.path.join(output_root, "GoodNotes")


def pdf_to_images(pdf_path, output_dir):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Convert PDF to images using pdf2image
    poppler_bin = os.path.join(os.path.dirname(current_directory), "poppler", "bin")

    images = pconvert.convert_from_path(pdf_path, dpi=300, poppler_path=poppler_bin)

    # Save each image to the output directory
    for idx, image in enumerate(images):
        image_file_path = os.path.join(output_dir, f'page_{idx + 1}.png')
        image.save(image_file_path)
        print(f"Page {idx + 1} saved as {image_file_path}")


def createNote(page, dir, note, notes, index, book_name):


    #setup image link
    page = page[:page.rfind(".")] + ".md"
    book = dir
    dir = os.path.join(dir, page)
    temp_dir = output_root.split("\\")
    temp_dir = "\\".join(temp_dir[:-1])
    new_dir = note.replace(temp_dir, "", 1).lstrip("\\")
    new_dir = new_dir.replace("\\", "/")


    #setup backlink base url
    backlink_base = new_dir.rfind("images")
    backlink_base = new_dir[:backlink_base]
    backlink_base = os.path.join(backlink_base, "Pages/")

    #string manipulation
    cIndex = book_name.rfind(".pdf")
    book_name = book_name[:cIndex]
    book_name = book_name.replace(" ", "_")


    with open(dir, 'w') as file:
        file.write("")

    with open(dir, "a") as file:
        file.write("#" + book_name + " ")


    for i in range(len(data["tags"])):
        cTag = data["tags"]
        with open(dir, 'a') as file:
            file.write("#" + cTag[i] + " ")

    if data["createBacklinks"] == True:

    #link page before
        bIndex = index - 1
        if bIndex >= 0:
            backlink = backlink_base + notes[bIndex]
            tIndex = backlink.rfind(".png")
            backlink = backlink[:tIndex]

            with open(dir, 'a') as file:
                file.write("[[" + backlink + "]] ")

    #link page after
        bIndex = index + 1
        if bIndex < len(notes):
            backlink = backlink_base + notes[bIndex]
            tIndex = backlink.rfind(".png")
            backlink = backlink[:tIndex]
            print(backlink)

            with open(dir, 'a') as file:
                file.write("[[" + backlink + "]] ")



    with open(dir, 'a') as file:
        file.write("![[" + new_dir + "]]")
        #string that links image file, then subtract the parent directory of output from it.


def main(folder_name):
    # Get a list of all PDF files in the input folder
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]

    cluster = os.path.join(output_root, folder_name)

    if not os.path.exists(cluster):
        os.makedirs(cluster)

    for pdf_file in pdf_files:
        pdf_file_path = os.path.join(input_folder, pdf_file)

        # Create a folder for each PDF

        journal_dir = os.path.join(cluster, os.path.splitext(pdf_file)[0])
        pdf_output_dir = os.path.join(journal_dir, "images")
        pdf_to_images(pdf_file_path, pdf_output_dir)
        notes = os.listdir(pdf_output_dir)

        note_output_dir = os.path.join(journal_dir, "Pages")
        os.makedirs(note_output_dir, exist_ok=True)


        index = 0
        for note in notes:
            note_path = os.path.join(pdf_output_dir, note)
            createNote(note, note_output_dir, note_path, notes, index, pdf_file)
            index += 1



if __name__ == "__main__":
    main()
