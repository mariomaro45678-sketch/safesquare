# How to Install PostGIS on Windows (PostgreSQL 16)

Since your system uses a local PostgreSQL 16 installation, the standard way to add PostGIS is via the **Application Stack Builder**.

### Step-by-Step Instructions:

1.  **Open Stack Builder**:
    - Press the **Windows Key** and type `Stack Builder`.
    - Open the app (it should be named "Application Stack Builder").

2.  **Select your Database**:
    - In the dropdown, select `PostgreSQL 16 on port 5432`.
    - Click **Next**.

3.  **Choose PostGIS**:
    - Expand the **Spatial Extensions** category.
    - Check the box for `PostGIS 3.5 Bundle for PostgreSQL 16 v3.5.x` (or the latest version shown).
    - Click **Next**.

4.  **Download**:
    - Choose a download folder (default is fine) and click **Next**.
    - Once downloaded, click **Next** to start the installation.

5.  **Installation Wizard**:
    - The PostGIS installer will pop up. Click **I Agree**.
    - On "Select Components", make sure **PostGIS** is checked.
    - Follow the prompts. If it asks to "Create a spatial database", you can select **No** (we will enable it on your existing `property_db`).
    - It may ask several times about registering environment variables (GDAL_DATA, etc.). Click **Yes** for all of them.

6.  **Finalize**:
    - Once the installer finishes, click **Close**.
    - Close Stack Builder.

### After Installation is Done:
Once you finish these steps, **tell me**, and I will run the final SQL command to activate it in your database!
