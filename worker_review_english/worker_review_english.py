import logging
import langid
logging.basicConfig(level=logging.CRITICAL)
from common.review_worker import  ReviewWorker
from common.model.review import Review

class EnglishWorker(ReviewWorker):
    def validate_review(self, review: Review):
        idioma, confianza = langid.classify(review.review_text)
        return (idioma == 'en')




