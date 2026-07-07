// Item-4 row-8 fixture: an enumeration-typed attribute. EnumerationUsage is a
// subtype of AttributeUsage; the AttributeUsage sweeps stay exact-type (opt-OUT),
// so the enum usage must NOT appear in an exact-type AttributeUsage query.
package EnumFixture {
    enum def Color { red; green; blue; }
    part def Painted {
        attribute shade : Color = Color::red;
    }
}
