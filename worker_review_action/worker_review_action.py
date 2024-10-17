import logging
logging.basicConfig(level=logging.CRITICAL)
from common.review_worker import  ReviewWorker

class ActionWorker(ReviewWorker):
    def validate_review(self, review):
        return review.is_action()