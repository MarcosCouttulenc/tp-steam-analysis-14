import logging
logging.basicConfig(level=logging.CRITICAL)
from common.review_worker import  ReviewWorker
from common.model.review import Review

class PositiveWorker(ReviewWorker):
    def validate_review(self, review: Review):
        return review.is_negative()