# Kobo Wifi Weather

A Kobo Wifi weather display, building on work from [this post](https://www.mobileread.com/forums/showthread.php?t=194376).

One of the problems with the original weather display is that the weather code no longer works. I've updated it to use OpenWeatherMap's API, and updated the "config" process to ask the user for a unit (from metric, imperial, or standard) in addition to their API key, which you can get for free.

I've also changed the cron job to run every 30 minutes.

For now, I've only included the files I've modified, with the fonts and icons available online and the rest of the files in the post. I'll add more if I spend more time on this.

**Please note that this is only tested to work on the Kobo Wifi.**

## Why

I had a spare Kobo Wifi, and e-ink displays cost far too much for me to just chuck it, so this is what I decided to do with it.

## How to use this

If you're also a proud owner of a hand-me-down Kobo Wifi that is somehow still working, you can follow these instructions to install this:

### Backup

**Backup first.** I cannot stress this enough - the following steps have the _very_ real chance of bricking your device, and you do not want to go through the hassle of looking for an image to restore to online. It's possible, but it's far easier if you have one available on hand.

To do so, one method is to follow the steps [here](https://wiki.mobileread.com/wiki/Kobo_WiFi_Hacking#Copying_the_micro_SD_card_on_Linux).

### Telnet/SSH

You next need to get telnet/ftp access, or something similar, to be able to launch code (at least easily):

- For telnet, follow the steps [here](https://wiki.mobileread.com/wiki/Kobo_WiFi_Hacking#Enabling_Telnet_.26_FTP). **Note that the default telnet has no password to root, and is insecure!**
- One of the comments [here](http://blog.ringerc.id.au/2011/01/enabling-telnet-and-ftp-access-to-kobo.html) details how you could get SSH running instead of an unsecure telnet.

### Install

#### Base files

Download the weather display files from the [above post](https://www.mobileread.com/forums/showthread.php?t=194376). Extract the tar file, and replace the files inside with the ones from this repo.

#### Weather icons

Download the weather icons from [here](https://erikflowers.github.io/weather-icons/), and convert the SVG files to PNG inside `mnt/onboard/.apps/koboWeather/icons`. To do this, for example:

```bash
mogrify -format png -path ../icons -colorspace sRGB -density 288  *.svg
```

You can use your own weather icons, but there are included OpenWeatherMap-to-Weather Icon mappings.

#### Font

You can also get the font (SF Pro Display) by just searching for it, or use your own.

#### Packaging and installation

Re-tar the file via:

```bash
tar czf KoboRoot.tgz mnt
```

Then plug in your Kobo Wifi to your PC, and move this `KoboRoot.tgz` into the `.kobo` folder. Eject and unplug your Kobo Wifi, and it will update with the correct code and reboot.

From there, follow the instructions from the post:

1. telnet/connect to your Kobo Wifi
2. To install then necessary dependencies:

```bash
/mnt/onboard/.python/install-python.sh
```

3. To run the weather application:

```bash
/mnt/onboard/.python/weather.sh
```

4. To automatically update:

```bash
/mnt/onboard/.apps/koboWeather/autoupdate.sh
```

5. To set the displayed temperature unit to Celsius (yeah it should be unified, too lazy):

```bash
echo C > /mnt/onboard/.apps/koboWeather/unit.txt
```

6. To prevent the Kobo from sleeping:

```bash
pkill nickel
```

#### If things go wrong

If anything goes wrong at any time, _restore from the backup_. This is why this is important.
