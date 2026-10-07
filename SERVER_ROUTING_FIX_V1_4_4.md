# V1.4.4 Server-Routed Direct Forms

Root cause correction: full approved forms are served as independent HTTP documents. The GEMS shell only routes the iframe to the original form URL. This removes the Android content:// dynamic-document rendering path used by V1.4.1–V1.4.3.
