(
    function () {
        var sbSiteSecret = "91895717-9f81-4543-8f46-c6307530668d";
        window.sitebehaviourTrackingSecret = sbSiteSecret;
        var scriptElement = document.createElement('script');
        scriptElement.async = true;
        scriptElement.id = "site-behaviour-script-v2";
        scriptElement.src = "https://sitebehaviour-cdn.fra1.cdn.digitaloceanspaces.com/index.min.js?sitebehaviour-secret=" + sbSiteSecret;
        document.head.appendChild(scriptElement);
    }
)()
;

(function (n, t, c) {
    var o = t.createElement("script");
    o.async = !0, o.src = "https://cdn.buttonizer.io/embed.js", o.onload = function () {
        window.Buttonizer.init(c)
    }, t.head.appendChild(o)
})(window, document, "1ffb16d9-ca6b-4fe2-85e0-d46cf510ca40");
