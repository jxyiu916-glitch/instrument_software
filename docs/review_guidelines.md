# Code Review Guidelines

## Performance Review Checklist

1. Timing & Performance
   - [ ] Timing constraints explicitly documented
   - [ ] Performance requirements specified
   - [ ] Critical paths identified
   - [ ] Hardware acceleration hooks present
   - [ ] Fallback paths available

2. Hardware Interface
   - [ ] Register interface clean and documented
   - [ ] Timing guarantees specified
   - [ ] Error handling complete
   - [ ] Hardware abstraction layer present
   - [ ] Mock implementations available

3. Resource Management
   - [ ] RAII principles followed in C++
   - [ ] Memory management explicit
   - [ ] Resource cleanup guaranteed
   - [ ] Error paths release resources
   - [ ] No resource leaks possible

## Architecture Review Checklist

1. Design Principles
   - [ ] Separation of concerns clear
   - [ ] Interfaces well-defined
   - [ ] Dependencies minimal and explicit
   - [ ] Extension points identified
   - [ ] Future requirements considered

2. C++/Python Integration
   - [ ] C++ migration path clear
   - [ ] Python reference implementation clean
   - [ ] pybind11 bindings complete
   - [ ] Error handling consistent
   - [ ] Performance contracts documented

3. Hardware Abstraction
   - [ ] Hardware dependencies isolated
   - [ ] Register map documented
   - [ ] Timing requirements clear
   - [ ] Error recovery specified
   - [ ] Test strategy documented

4. Real-time Considerations
   - [ ] Real-time constraints documented
   - [ ] Critical paths identified
   - [ ] Interrupt handling specified
   - [ ] Timing guarantees clear
   - [ ] Performance measurements present

## Testing Review Checklist

1. Coverage
   - [ ] Unit tests complete
   - [ ] Hardware interface tests present
   - [ ] Timing tests included
   - [ ] Error conditions covered
   - [ ] Performance tests added

2. Test Infrastructure
   - [ ] Mock objects available
   - [ ] Timing simulation possible
   - [ ] Hardware simulation complete
   - [ ] Error injection supported
   - [ ] CI integration clear

## PR Template

```markdown
## Description
[Description of the change]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Performance improvement
- [ ] Hardware interface
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Hardware interface tested
- [ ] Performance validated
- [ ] Error conditions verified

## Performance Impact
- [ ] Timing requirements met
- [ ] Resource usage acceptable
- [ ] No performance regression

## Documentation
- [ ] API documentation updated
- [ ] Design docs updated
- [ ] ADRs added/updated
- [ ] Comments clear and complete
```