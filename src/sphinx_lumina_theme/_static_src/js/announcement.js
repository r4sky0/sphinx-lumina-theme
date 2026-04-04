export default function announcementBanner() {
  let _id = null;
  return {
    init() {
      _id = this.$el.getAttribute("data-announcement-id");
    },

    dismiss() {
      if (_id) {
        localStorage.setItem("lumina-announce-" + _id, "1");
      }
      document.documentElement.classList.remove("has-announcement");
    },
  };
}
