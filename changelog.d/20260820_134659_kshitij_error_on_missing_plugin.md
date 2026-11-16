- [Feature] `tutor` now treats a missing plugin as an error and will now return 
  a non-zero exit code if a plugin fails to load. This ensures that a missing 
  or broken plugin stops deployment instead of potentially leading to a broken 
  deployment (by @xitij2000)
