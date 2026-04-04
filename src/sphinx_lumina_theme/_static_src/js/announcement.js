export default function announcementBanner() {
  return {
    dismissed: false,

    init() {
      const id = this.$el.getAttribute("data-announcement-id");
      if (id && localStorage.getItem("lumina-announce-" + id) === "1") {
        this.dismissed = true;
      } else {
        // Defer measurement until after Alpine removes x-cloak and
        // the browser has reflowed — offsetHeight is 0 during init()
        this.$nextTick(() => this._updateOffset());
      }
    },

    dismiss() {
      const id = this.$el.getAttribute("data-announcement-id");
      if (id) {
        localStorage.setItem("lumina-announce-" + id, "1");
      }
      this.dismissed = true;
      document.documentElement.style.setProperty("--lumina-announce-h", "0px");
    },

    _updateOffset() {
      // Measure banner height and push the fixed header down
      const h = this.$el.offsetHeight;
      document.documentElement.style.setProperty(
        "--lumina-announce-h",
        h + "px"
      );
    },
  };
}
