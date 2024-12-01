function showTab(tabId) {
  // Update the URL fragment
  window.location.hash = tabId;

  // Trigger Bootstrap's tab change behavior
  var tabLink = document.querySelector(`#${tabId}-tab`);
  var tab = new bootstrap.Tab(tabLink);  // Avoid naming conflict by renaming the variable
  tab.show();
}

window.onload = function() {
  const hash = window.location.hash.slice(1);  // Get the fragment without the '#'
  if (hash === 'register' || hash === 'login') {
      showTab(hash); // Show the corresponding tab based on the fragment
  } else {
      showTab('login'); // Default to the login tab
  }
};
