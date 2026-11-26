# Seodaemun Church website

Upload the extracted contents to the root of your GitHub repository, including the hidden `.github` folder. In **Settings → Pages → Build and deployment**, select **GitHub Actions**. Push a commit to the default branch to publish the bundled homepage. You can also start **Actions → Church website → Run workflow** to check the latest sermon and publish.

## Files

- `index.html` and `news.html` contain the homepage and church news.
- `css/` and `js/` contain the stylesheet and browser interactions.
- `assets/images/` and `assets/fonts/` contain the photographs, fonts and font license.
- `scripts/update_sermon.py` reads the church's YouTube feed and updates the marked sermon section in the root homepage.
- `.github/workflows/pages.yml` deploys the site and schedules the sermon check for Mondays at 08:00 Korea time. Scheduled start times can vary.

The workflow needs permission to push sermon changes to the default branch and deploy to the github-pages environment. If repository rules block a run, check its Actions log. A failed feed check stops that run before deployment.

To preview, run `python3 -m http.server 8000` from this directory and open http://localhost:8000/.
