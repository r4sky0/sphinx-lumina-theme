export default function announcementBanner() {
  return {
    dismissed: false,

    init() {
      const id = this.$el.getAttribute("data-announcement-id");
      if (id && localStorage.getItem("lumina-announce-" + id) === "1") {
        this.dismissed = true;
        document.documentElement.classList.remove("has-announcement");
      }
    },

    dismiss() {
      const id = this.$el.getAttribute("data-announcement-id");
      if (id) {
        localStorage.setItem("lumina-announce-" + id, "1");
      }
      this.dismissed = true;
      document.documentElement.classList.remove("has-announcement");
    },
  };
}
