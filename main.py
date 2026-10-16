import sources.devpost as devpost
import sources.brabble as brabble
import sources.lablab as lablab
import sources.kaggle as kaggle
import config
import filters
import storage
import notify


def run() -> None:
    all_hackathons = []
    sources = [devpost, lablab, kaggle] + ([brabble] if config.BRABBLE_API_KEY else [])
    for source in sources:
        try:
            all_hackathons.extend(source.fetch_hackathons())
        except Exception as e:
            print(f"Warning: {source.__name__} failed: {e}")
    new_hackathons = []
    for h in all_hackathons:
        if storage.is_notified(h["id"]):
            continue
        if not filters.apply_all(h):
            continue
        new_hackathons.append(h)
    if new_hackathons and notify.send_summary(new_hackathons):
        for h in new_hackathons:
            storage.mark_notified(h["id"])


if __name__ == "__main__":
    run()
