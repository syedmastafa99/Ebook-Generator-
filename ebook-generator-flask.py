from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
from ebooklib import epub
import markdown2
import uuid
import tempfile

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'development-key')
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_ebook():
    # Get form data
    title = request.form.get('title', 'Untitled')
    author = request.form.get('author', 'Anonymous')
    content = request.form.get('content', '')
    format_type = request.form.get('format', 'epub')
    
    if not content:
        flash('Please provide some content for your ebook.')
        return redirect(url_for('index'))
    
    # Create a unique filename
    filename = f"{uuid.uuid4()}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Generate ebook
    if format_type == 'epub':
        book = epub.EpubBook()
        book.set_title(title)
        book.add_author(author)
        
        # Convert Markdown to HTML
        html_content = markdown2.markdown(content)
        
        # Add chapter
        chapter = epub.EpubHtml(title=title, file_name='chapter.xhtml')
        chapter.content = f'<html><body>{html_content}</body></html>'
        book.add_item(chapter)
        
        # Add default NCX and Nav
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Define Table of Contents
        book.toc = [epub.Link('chapter.xhtml', title, 'chapter')]
        
        # Add spine
        book.spine = ['nav', chapter]
        
        # Create the EPUB file
        epub.write_epub(f"{output_path}.epub", book)
        
        return send_file(
            f"{output_path}.epub",
            as_attachment=True,
            download_name=f"{title.replace(' ', '_')}.epub",
            mimetype='application/epub+zip'
        )
    else:
        flash('Only EPUB format is currently supported.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
