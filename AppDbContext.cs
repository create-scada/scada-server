using Microsoft.EntityFrameworkCore;
using Scada.Models;

namespace Scada;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options)
        : base(options)
    {
    }

    public DbSet<Location> Locations { get; set; }
    public DbSet<Device> Devices { get; set; }
    public DbSet<DisplayPoint> DisplayPoints { get; set; }
    public DbSet<Reading> Readings { get; set; }
}