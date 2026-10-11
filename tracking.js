/* HTE shared tracking: GA4 outbound click events + optional Meta Pixel.
 * Loaded on every page. Needs the GA4 gtag snippet in <head> (G-5JVQNQXHXW).
 * Meta Pixel: paste the Pixel ID below. While it is empty, nothing is sent to Meta. */
(function () {
  if (window.__hteTracking) return;
  window.__hteTracking = true;

  var META_PIXEL_ID = ''; // e.g. '1234567890123456' (Meta Events Manager > Data sources)

  /* ---- Meta Pixel (only when an ID is set) ---- */
  if (META_PIXEL_ID) {
    !function (f, b, e, v, n, t, s) {
      if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
      if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = [];
      t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
    }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', META_PIXEL_ID);
    fbq('track', 'PageView');
  }

  /* ---- Outbound link classification ---- */
  var BOOKING = [
    [/getyourguide\.com|gyg\.me/i, 'getyourguide'],
    [/viator\.com/i, 'viator'],
    [/klook\.com/i, 'klook'],
    [/kkday\.com/i, 'kkday']
  ];

  function tourFromUrl(href) {
    var m = /[?&]cmp=([^&#]+)/.exec(href); // e.g. hte-lp-totoro, hte-blog-hanno-top
    return m ? decodeURIComponent(m[1]) : '';
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a');
    if (!a || !a.href) return;
    var href = a.href, category = null, platform = '', i;

    for (i = 0; i < BOOKING.length; i++) {
      if (BOOKING[i][0].test(href)) { category = 'booking_click'; platform = BOOKING[i][1]; break; }
    }
    if (!category) {
      if (/instagram\.com/i.test(href)) category = 'instagram_click';
      else if (/substack\.com/i.test(href)) category = 'substack_click';
      else if (/upwork\.com/i.test(href)) category = 'itinerary_click';
      else if (href.indexOf('mailto:') === 0) category = 'email_click';
      else if (/#custom-request/.test(href) && a.classList.contains('ask-link')) category = 'custom_request_click';
    }
    if (!category) return;

    var params = {
      link_text: (a.textContent || '').trim().slice(0, 60),
      link_url: href,
      page_location: window.location.href,
      transport_type: 'beacon' // survives navigation to the booking site
    };
    if (platform) { params.platform = platform; params.cta = tourFromUrl(href); }

    if (typeof gtag === 'function') gtag('event', category, params);
    if (category === 'booking_click' && typeof fbq === 'function') {
      fbq('trackCustom', 'BookingClick', { platform: platform, cta: params.cta });
    }
  }, true);
})();
