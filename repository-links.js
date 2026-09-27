// Resolve public contacts from one deployment setting; no credentials or local APIs.
try {
  const response = await fetch(new URL('./public-repository.json', import.meta.url));
  if (!response.ok) throw Error('Repository setting unavailable');
  const config = await response.json();
  let repository = config.repository;
  // Forks hosted on GitHub project Pages follow their own owner/repository.
  if (location.hostname.endsWith('.github.io')) {
    const owner = location.hostname.slice(0, -'.github.io'.length);
    const name = location.pathname.split('/').filter(Boolean)[0];
    if (name) repository = `${owner}/${name}`;
  }
  if (typeof repository !== 'string' || !/^[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+$/.test(repository)) throw Error('Invalid repository setting');
  const paths = {proposal:'/issues/new?template=visitor-proposal.yml',inbox:'/issues',source:''};
  document.querySelectorAll('[data-repository-link]').forEach(link => {
    const key = link.dataset.repositoryLink;
    if (!Object.hasOwn(paths,key)) return;
    link.href = new URL(`/${repository}${paths[key]}`, 'https://github.com').href;
    link.removeAttribute('aria-disabled');
  });
} catch {
  document.querySelectorAll('[data-repository-link]').forEach(link => {
    link.removeAttribute('href'); link.setAttribute('aria-disabled','true');
    link.textContent += ' (unavailable; use the email contact)';
  });
}
