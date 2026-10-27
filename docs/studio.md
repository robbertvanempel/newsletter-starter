# Create an edition in Newsletter Studio

1. Open your Studio URL and log in. For a local preview, start `python3 -m http.server 8787 --bind 127.0.0.1 --directory studio` from the repository root and open `http://127.0.0.1:8787`. The local server is bound to your own computer only.
2. Replace the newsletter name, subject, preview text, introduction, accent colour and organisation/postal-address footer.
3. Edit your first story. Add more with **+ Add story**, move them with the arrow buttons and remove a block with ×. Text is deliberately plain text; the exporter escapes HTML and Liquid entered in content fields. Blank lines become paragraphs.
4. Add a full HTTPS article link and link label. Images are optional and need a **public HTTPS URL** and an image description. Upload a non-private image to your own Keila media storage or other chosen host and use its actual public URL. Do not use a local file path, expiring signed URL or image containing subscriber information. Studio has no upload API and no credentials.
5. Switch between **Desktop** and **Mobile** previews. This is a browser preview, not a guarantee that every email client renders identically. Send an approved inbox test from Keila before using the layout for subscribers.
6. Click **Save editable file**. The downloaded `.source.json` can be reopened with **Open editable file** on another computer. **New edition** resets the editor after confirmation.
7. Click **Export email HTML** for the standalone inline-styled email, or **Export Keila draft** for a JSON payload accepted by the draft helper.
8. Import the JSON using the command in INSTALL.md. The token belongs only at the helper's hidden terminal prompt. In Keila, review the new private campaign, choose the correct sender and audience, and use Keila to test, schedule or send after owner approval.

The real email retains `{{ unsubscribe_link }}`, which Keila replaces for the recipient. Never remove it or replace it with a fixed person's unsubscribe URL. The browser preview uses a dummy link. Keila handles delivery, opt-out and any enabled tracking; the starter exports `do_not_track: true` by default.

## Draft storage

Autosave uses localStorage in the current browser. It is not a server backup or a Keila sync. A different browser, a cleared profile or another Studio hostname will not have that draft. Shared browser profiles can expose local drafts to their users, even if Studio itself requires login. Use your own profile, save source files privately and remove them when no longer needed.

The importer creates a private receipt under `.private/`. A byte-equivalent normalized payload and same Keila origin reuse the successful receipt. Keep that directory private. If a request has an uncertain result, the importer refuses an automatic retry: inspect Keila for the subject and time before deciding whether to remove only that receipt. Do not repeatedly import a changed file expecting it to overwrite an older campaign. Native Keila remains the owner of an imported campaign.
