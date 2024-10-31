import logging
logging.basicConfig(level=logging.CRITICAL)
from common.review_worker import  ReviewWorker
from common.model.review import Review

class IndieReviewWorker(ReviewWorker):
    def validate_review(self, review: Review):
        if review.is_indie():
            print("Reseña indie")
        return review.is_indie()