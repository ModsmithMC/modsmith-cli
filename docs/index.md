# Modsmith command line

```{raw} html
<div class="hero">
  <picture>
    <source media="(max-width: 560px)" srcset="_static/hero-cli-small.svg">
    <img src="_static/hero-cli.svg" alt="">
  </picture>
  <div class="hero-copy">
    <h2>Modpacks from your terminal</h2>
    <p>Modsmith's command line installs modpacks, mods, resource packs and shaders from Modrinth and CurseForge, and adds them to the official Minecraft launcher.</p>
    <div class="actions">
      <a class="button primary" href="#install">Install it</a>
      <a class="button" href="get-started/quickstart/">Quick start</a>
    </div>
  </div>
</div>

<div class="band" id="install">
  <div class="band-inner single">
    <p class="eyebrow">Install</p>
    <h2>Two commands, and you are set</h2>
    <p class="lede-left">uv brings the Python that Modsmith needs, so there is nothing else to install first.</p>
    <div class="tabs install" data-tabs>
      <div class="tab-list" role="tablist">
        <button type="button" role="tab" data-tab="windows">Windows</button>
        <button type="button" role="tab" data-tab="macos">macOS</button>
        <button type="button" role="tab" data-tab="linux">Linux</button>
      </div>
      <div class="tab-panel" role="tabpanel" data-panel="windows">
        <ol class="install-steps">
          <li><p><strong>Install uv.</strong> In PowerShell:</p>
            <div class="highlight-powershell notranslate"><div class="highlight"><pre>powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"</pre></div></div></li>
          <li><p><strong>Install Modsmith</strong>, in a new PowerShell window:</p>
            <div class="highlight-powershell notranslate"><div class="highlight"><pre>uv tool install modsmith-cli</pre></div></div></li>
        </ol>
      </div>
      <div class="tab-panel" role="tabpanel" data-panel="macos" hidden>
        <ol class="install-steps">
          <li><p><strong>Install uv.</strong> In Terminal:</p>
            <div class="highlight-bash notranslate"><div class="highlight"><pre>curl -LsSf https://astral.sh/uv/install.sh | sh</pre></div></div></li>
          <li><p><strong>Install Modsmith</strong>, in a new Terminal window:</p>
            <div class="highlight-bash notranslate"><div class="highlight"><pre>uv tool install modsmith-cli</pre></div></div></li>
        </ol>
      </div>
      <div class="tab-panel" role="tabpanel" data-panel="linux" hidden>
        <ol class="install-steps">
          <li><p><strong>Install uv:</strong></p>
            <div class="highlight-bash notranslate"><div class="highlight"><pre>curl -LsSf https://astral.sh/uv/install.sh | sh</pre></div></div></li>
          <li><p><strong>Install Modsmith</strong>, in a new terminal:</p>
            <div class="highlight-bash notranslate"><div class="highlight"><pre>uv tool install modsmith-cli</pre></div></div></li>
        </ol>
      </div>
    </div>
    <p class="install-more">Upgrading, Tab completion and other ways to install are in the <a href="get-started/installation/">installation guide</a>.</p>
  </div>
</div>

<div class="band alternate">
  <div class="band-inner showcase">
    <div class="band-copy">
      <p class="eyebrow">Play</p>
      <h2>From a name to a game</h2>
      <ol class="steps">
        <li><strong>Install a pack</strong> Name a modpack from Modrinth or CurseForge, or give a file. Modsmith shows what it will add, and asks.</li>
        <li><strong>Open the launcher</strong> The pack has its own installation, with its icon, Minecraft version and mod loader ready.</li>
        <li><strong>Play</strong> Choose it and press Play. Your other installations stay as they were.</li>
      </ol>
    </div>
    <div class="showcase-media">
      <div class="terminal" id="install-demo" data-terminal aria-label="Modsmith installing a modpack">
        <div class="terminal-bar"><span></span><span></span><span></span></div>
<pre data-command="modsmith install fabulously-optimized --name survival"><span class="prompt">$ </span><span class="typed"></span>
<span class="out">Install Fabulously Optimized 14.1.2 as survival
  <b class="add">+</b> mods/BetterGrassify-1.8.7+fabric.26.2.jar
  <b class="add">+</b> mods/ImmediatelyFast-Fabric-1.16.5+26.2.jar
  <b class="add">+</b> mods/cloth-config-26.2.155.jar
  <b class="add">+</b> and 99 more
<strong>102 to add; 45.0 MB to download.</strong>
Minecraft 26.2 with Fabric 0.20.1, and an installation in the official
launcher.
Install it? [Y/n]: y
Installed Fabulously Optimized as survival. In the official launcher,
choose the Fabulously Optimized installation and play.</span></pre>
      </div>
      <div class="launcher-demo" data-follows="install-demo" aria-label="The installation appears in the official launcher">
        <div class="launcher-bar">Official launcher</div>
        <div class="launcher-body">
          <ul>
            <li class="new"><i class="icon-pack"></i><b>Fabulously Optimized</b><em>New</em><small>fabric-loader-0.20.1-26.2</small></li>
            <li><i class="icon-grass"></i><b>Latest release</b><small>26.3</small></li>
            <li><i class="icon-dirt"></i><b>Latest snapshot</b><small>26.4-snapshot-7</small></li>
          </ul>
          <span class="launcher-play">Play</span>
          <p class="launcher-status" data-status></p>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="band">
  <div class="band-inner">
    <div class="band-copy">
      <p class="eyebrow">Find</p>
      <h2>Search both platforms</h2>
      <p>Search Modrinth and CurseForge from one place, sorted the way you like. Each result shows the name to give other commands.</p>
    </div>
    <div class="terminal" data-terminal aria-label="Modsmith searching for mods">
      <div class="terminal-bar"><span></span><span></span><span></span></div>
<pre data-command="modsmith search sodium --limit 3"><span class="prompt">$ </span><span class="typed"></span>
<span class="out"><strong>Sodium</strong>  <span class="dim">258.9M downloads</span>
  <b class="add">modrinth:sodium</b>
<strong>Sodium Extra</strong>  <span class="dim">109.2M downloads</span>
  <b class="add">modrinth:sodium-extra</b>
<strong>Reese's Sodium Options</strong>  <span class="dim">90.5M downloads</span>
  <b class="add">modrinth:reeses-sodium-options</b>
<span class="dim">Showing 3 of 108.</span></span></pre>
    </div>
  </div>
</div>

<div class="band alternate flip">
  <div class="band-inner">
    <div class="band-copy">
      <p class="eyebrow">Add</p>
      <h2>The mods they need come along</h2>
      <p>Add mods, resource packs and shaders to any instance. Dependencies are found and installed, and removed again when nothing needs them.</p>
    </div>
    <div class="terminal" data-terminal aria-label="Modsmith adding a mod with its dependency">
      <div class="terminal-bar"><span></span><span></span><span></span></div>
<pre data-command="modsmith add survival jei"><span class="prompt">$ </span><span class="typed"></span>
<span class="out">Add to survival
  <b class="add">+</b> mods/mezz_config-26.2-fabric-0.6.10.jar
  <b class="add">+</b> mods/jei-26.2-fabric-30.42.0.236.jar
    <span class="dim">MezzConfig comes too, because a mod needs it</span>
<strong>2 to add; 2.8 MB to download.</strong>
Add them? [Y/n]: y
Added to survival.</span></pre>
    </div>
  </div>
</div>

<div class="band">
  <div class="band-inner">
    <div class="band-copy">
      <p class="eyebrow">Update</p>
      <h2>Updates that keep your changes</h2>
      <p>See what changed in the new release, and every file it touches. Files you edited stay as they are, and a new Minecraft version moves the launcher installation with it.</p>
    </div>
    <div class="terminal" data-terminal aria-label="Modsmith updating a modpack">
      <div class="terminal-bar"><span></span><span></span><span></span></div>
<pre data-command="modsmith update survival"><span class="prompt">$ </span><span class="typed"></span>
<span class="out"><strong>What changed in 14.1.2 for 26.2</strong>
<span class="dim">- Backported Crash Assistant config updates
- Updated Fabric Loader to 0.20.1</span>
Update Fabulously Optimized 13.6.0 to Fabulously Optimized 14.1.2
  <b class="add">+</b> mods/ImmediatelyFast-Fabric-1.16.5+26.2.jar
  <b class="add">+</b> and 43 more
  <b class="change">~</b> config/modpack_defaults/options.txt
  <b class="change">~</b> and 18 more
  <b class="remove">-</b> mods/ImmediatelyFast-Fabric-1.15.3+26.1.jar
  <b class="remove">-</b> and 41 more
<strong>44 to add, 19 to update, 42 to remove; 35.8 MB to download.</strong>
It moves from Minecraft 26.1.2 with Fabric 0.19.5 to Minecraft 26.2 with
Fabric 0.20.1.
Update them? [Y/n]: y
Updated survival.</span></pre>
    </div>
  </div>
</div>

<div class="band alternate center">
  <div class="band-inner">
    <p class="eyebrow">Load</p>
    <h2>Every major mod loader</h2>
    <p class="lede">Modsmith installs the loader a pack needs, or the version you choose.</p>
    <div class="loaders">
      <div class="loader"><strong>Forge</strong><span>1.13.2 and later</span></div>
      <div class="loader"><strong>NeoForge</strong><span>1.20.1 and later</span></div>
      <div class="loader"><strong>Fabric</strong><span>1.14 and later</span></div>
      <div class="loader"><strong>Quilt</strong><span>1.14.4 and later</span></div>
    </div>
  </div>
</div>

<div class="band flip">
  <div class="band-inner">
    <div class="band-copy">
      <p class="eyebrow">Bring your own</p>
      <h2>Take over what you made</h2>
      <p>Already set up an installation in the launcher by hand? Import it, and Modsmith recognises its mods so they can be updated.</p>
    </div>
    <div class="terminal" data-terminal aria-label="Modsmith importing an installation">
      <div class="terminal-bar"><span></span><span></span><span></span></div>
<pre data-command='modsmith import "My Fabric world"'><span class="prompt">$ </span><span class="typed"></span>
<span class="out">Import My Fabric world as my-fabric-world: Minecraft 26.2 with Fabric
0.20.1, in D:\Games\my-fabric-world.
Import it? [Y/n]: y
  Sodium: mods/sodium-fabric-0.9.2+mc26.2.jar
  Sodium Extra: mods/sodium-extra-fabric-0.9.5+mc26.2.jar
  Entity Culling: mods/entityculling-fabric-1.11.3-mc26.2.jar
3 files can now be updated and removed like added ones.
my-fabric-world is now an instance.</span></pre>
    </div>
  </div>
</div>

<div class="band alternate">
  <div class="band-inner single">
    <p class="eyebrow">Start here</p>
    <h2>Three steps to your first game</h2>
    <div class="path">
      <a href="get-started/installation/"><b>1</b><strong>Install Modsmith</strong><span>Two commands on Windows, macOS or Linux.</span></a>
      <a href="get-started/quickstart/"><b>2</b><strong>Install a modpack</strong><span>From a name to playing, in five minutes.</span></a>
      <a href="guides/"><b>3</b><strong>Make it yours</strong><span>Add mods and shaders, and keep them up to date.</span></a>
    </div>
    <div class="task-groups">
      <div>
        <h3>Play</h3>
        <a href="guides/modpacks/">Install a modpack</a>
        <a href="guides/curseforge/">Install from CurseForge</a>
        <a href="guides/existing/">Take over an installation you made</a>
      </div>
      <div>
        <h3>Change what you play</h3>
        <a href="guides/mods/">Add mods, resource packs and shaders</a>
        <a href="guides/mods/#turn-files-off">Turn a mod off</a>
        <a href="guides/updates/">Update a pack and what you added</a>
      </div>
      <div>
        <h3>Look things up</h3>
        <a href="reference/commands/">Every command</a>
        <a href="reference/settings/">Settings</a>
        <a href="concepts/">How Modsmith works</a>
      </div>
    </div>
  </div>
</div>

<div class="band center closing">
  <div class="band-inner">
    <h2>Something not working?</h2>
    <p class="lede">Most messages have an answer on the troubleshooting page.</p>
    <div class="actions">
      <a class="button primary" href="help/troubleshooting/">Troubleshooting</a>
      <a class="button" href="help/faq/">Questions people ask</a>
    </div>
  </div>
</div>
```

```{toctree}
:hidden:
:caption: Get started

get-started/index
```

```{toctree}
:hidden:
:caption: Guides

guides/index
```

```{toctree}
:hidden:
:caption: Concepts

concepts/index
```

```{toctree}
:hidden:
:caption: Reference

reference/index
```

```{toctree}
:hidden:
:caption: Help

help/index
```
