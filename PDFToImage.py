from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
from PIL import Image
import fitz, re, os


class GetPic:
    def __init__(self, filename, password=''):
        with open(filename, 'rb') as file:
            self.parser = PDFParser(file)
        self.doc = PDFDocument()
        self.parser.set_document(self.doc)
        self.doc.set_parser(self.parser)
        self.doc.initialize(password)
        if not self.doc.is_extractable:
            raise PDFTextExtractionNotAllowed
        else:
            self.resource_manager = PDFResourceManager()
            self.laparams = LAParams()
            self.device = PDFPageAggregator(self.resource_manager, laparams=self.laparams)
            self.interpreter = PDFPageInterpreter(self.resource_manager, self.device)
            self.doc_pdfs = list(self.doc.get_pages())
        self.doc_pics = fitz.open(filename)

    def to_pic(self, doc, zoom, pg, pic_path):
        rotate = int(0)
        trans = fitz.Matrix(zoom, zoom).preRotate(rotate)
        pm = doc.getPixmap(matrix=trans, alpha=False)
        path = os.path.join(pic_path, str(pg)) + '.png'
        pm.writePNG(path)
        return path

    def get_pic_loc(self, doc, search01, search02):
        self.interpreter.process_page(doc)
        layout = self.device.get_result()
        canvas_size = layout.bbox
        loc_top = []
        loc_bottom = []
        loc_named_pic = []
        for i in layout:
            if hasattr(i, 'get_text'):
                text = i.get_text().strip()
                if re.search(search01, text):
                    loc_top.append((i.bbox, text))
                elif re.search(search02, text):
                    loc_bottom.append((i.bbox, text))
        zip_loc = zip(loc_top, loc_bottom)

        for i in zip_loc:
            y1 = i[1][0][1]
            y2 = i[0][0][3]
            name = i[0][1]
            loc_named_pic.append((name, (y1, y2)))
        return loc_named_pic, canvas_size

    def get_crops(self, pic_path, canvas_size, position, cropped_pic_name, cropped_pic_path):
        img = Image.open(pic_path)
        pic_size = img.size
        size_increase = 10
        x1 = 0
        x2 = pic_size[0]
        y1 = pic_size[1] * (1 - (position[1] + size_increase)/canvas_size[3])
        y2 = pic_size[1] * (1 - (position[0] - size_increase)/canvas_size[3])
        cropped_img = img.crop((x1, y1, x2, y2))
        path = os.path.join(cropped_pic_path, cropped_pic_name) + '.png'
        cropped_img.save(path)

    def To_Image(self, pic_path, cropped_pic_path, top_ord, bottom_ord):
        page_count = self.doc_pics.pageCount
        search01 = top_ord
        search02 = bottom_ord
        for pg in range(page_count):
            doc_pdf = self.doc_pdfs[pg]
            doc_pic = self.doc_pics[pg]
            path = self.to_pic(doc_pic, 2, pg+1, pic_path)
            loc_name_pic, canvas_size = self.get_pic_loc(doc_pdf, search01, search02)
            if not loc_name_pic:
                return
            for i in loc_name_pic:
                position = i[1]
                cropped_pic_name = str(pg+1) + '-' + str(loc_name_pic.index(i) + 1)
                print(cropped_pic_name)
                self.get_crops(path, canvas_size, position, cropped_pic_name, cropped_pic_path)


def main(pdf_path, pic_path, cropped_pic_path, top_ord, bottom_ord):
    test = GetPic(pdf_path)
    test.To_Image2(pic_path, cropped_pic_path, top_ord, bottom_ord)


